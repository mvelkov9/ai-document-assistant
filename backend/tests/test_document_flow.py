from io import BytesIO

from app.services import document_service as document_service_module
from app.services import pdf_service as pdf_service_module
from app.services import processing_service as processing_service_module
from app.services import summary_service as summary_service_module


def register_and_login(client, email='flow@example.com'):
    client.post(
        '/api/v1/auth/register',
        json={
            'email': email,
            'password': 'VerySecure123',
            'full_name': 'Flow User',
        },
    )
    login_response = client.post(
        '/api/v1/auth/login',
        json={
            'email': email,
            'password': 'VerySecure123',
        },
    )
    token = login_response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_upload_document(client, monkeypatch) -> None:
    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )

    headers = register_and_login(client, email='upload@example.com')
    files = {'file': ('sample.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')}
    response = client.post('/api/v1/documents/upload', headers=headers, files=files)

    assert response.status_code == 201
    assert response.json()['original_filename'] == 'sample.pdf'


def test_summarize_document(client, monkeypatch) -> None:
    async def fake_summarize(self, text):
        return 'Short generated summary.'

    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )
    monkeypatch.setattr(
        document_service_module.StorageService,
        'download_bytes',
        lambda self, object_name: b'%PDF-1.4 downloaded',
    )
    monkeypatch.setattr(
        pdf_service_module.PdfService,
        'extract_text',
        lambda self, content: 'This document explains the semester project architecture.',
    )
    monkeypatch.setattr(
        summary_service_module.SummaryService,
        'summarize',
        fake_summarize,
    )

    headers = register_and_login(client, email='summary@example.com')
    upload_response = client.post(
        '/api/v1/documents/upload',
        headers=headers,
        files={'file': ('summary.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')},
    )
    document_id = upload_response.json()['id']

    response = client.post(f'/api/v1/documents/{document_id}/summarize', headers=headers)

    assert response.status_code == 200
    assert response.json()['summary_text'] == 'Short generated summary.'
    assert response.json()['processing_status'] == 'ready'


def test_ask_document_question(client, monkeypatch) -> None:
    async def fake_answer_question(self, text, question):
        return ('The main focus is secure upload and AI summary features.', 'fallback')

    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )
    monkeypatch.setattr(
        document_service_module.StorageService,
        'download_bytes',
        lambda self, object_name: b'%PDF-1.4 downloaded',
    )
    monkeypatch.setattr(
        pdf_service_module.PdfService,
        'extract_text',
        lambda self, content: 'The document focuses on secure upload and AI summary features.',
    )
    monkeypatch.setattr(
        summary_service_module.SummaryService,
        'answer_question',
        fake_answer_question,
    )

    headers = register_and_login(client, email='qa@example.com')
    upload_response = client.post(
        '/api/v1/documents/upload',
        headers=headers,
        files={'file': ('qa.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')},
    )
    document_id = upload_response.json()['id']

    response = client.post(
        f'/api/v1/documents/{document_id}/ask',
        headers=headers,
        json={'question': 'Kaj je glavni fokus dokumenta?'},
    )

    assert response.status_code == 200
    assert response.json()['source_mode'] == 'fallback'
    assert 'secure upload' in response.json()['answer_text']


def test_create_summary_job(client, monkeypatch) -> None:
    async def fake_run_summary_job(self, job_id):
        return None

    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )
    monkeypatch.setattr(
        processing_service_module.ProcessingService,
        'run_summary_job',
        fake_run_summary_job,
    )

    headers = register_and_login(client, email='jobs@example.com')
    upload_response = client.post(
        '/api/v1/documents/upload',
        headers=headers,
        files={'file': ('job.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')},
    )
    document_id = upload_response.json()['id']

    response = client.post(f'/api/v1/documents/{document_id}/summarize-jobs', headers=headers)

    assert response.status_code == 202
    assert response.json()['job_type'] == 'summary'
    assert response.json()['status'] == 'queued'


def test_create_question_job(client, monkeypatch) -> None:
    async def fake_run_question_job(self, job_id):
        return None

    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )
    monkeypatch.setattr(
        processing_service_module.ProcessingService,
        'run_question_job',
        fake_run_question_job,
    )

    headers = register_and_login(client, email='questionjobs@example.com')
    upload_response = client.post(
        '/api/v1/documents/upload',
        headers=headers,
        files={'file': ('job-question.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')},
    )
    document_id = upload_response.json()['id']

    response = client.post(
        f'/api/v1/documents/{document_id}/ask-jobs',
        headers=headers,
        json={'question': 'Kaj je jedro dokumenta?'},
    )

    assert response.status_code == 202
    assert response.json()['job_type'] == 'question'
    assert response.json()['job_input'] == 'Kaj je jedro dokumenta?'


def test_get_question_job_status(client, monkeypatch) -> None:
    async def fake_run_question_job(self, job_id):
        return None

    monkeypatch.setattr(
        document_service_module.StorageService,
        'upload_bytes',
        lambda self, object_name, content, content_type: None,
    )
    monkeypatch.setattr(
        processing_service_module.ProcessingService,
        'run_question_job',
        fake_run_question_job,
    )

    headers = register_and_login(client, email='questionstatus@example.com')
    upload_response = client.post(
        '/api/v1/documents/upload',
        headers=headers,
        files={'file': ('job-status.pdf', BytesIO(b'%PDF-1.4 sample'), 'application/pdf')},
    )
    document_id = upload_response.json()['id']

    create_response = client.post(
        f'/api/v1/documents/{document_id}/ask-jobs',
        headers=headers,
        json={'question': 'Kaj je povzetek dokumenta?'},
    )

    assert create_response.status_code == 202

    job_id = create_response.json()['id']
    status_response = client.get(f'/api/v1/jobs/{job_id}', headers=headers)

    assert status_response.status_code == 200
    assert status_response.json()['id'] == job_id
    assert status_response.json()['job_type'] == 'question'
    assert status_response.json()['status'] == 'queued'
