# Phase 01 - Scope and Scenario

## Purpose

Define a concrete semester project scenario that is technically strong enough for MOZNOST 3 and realistic enough to be implemented incrementally.

## Selected scenario

The project implements a secure web service for a small Slovenian organization that stores internal PDF documents and helps authenticated users generate summaries and ask short follow-up questions about one selected document.

## Core problem

Small teams often keep documents in scattered folders and spend too much time searching or skimming internal reports, specifications, and procedures. The project centralizes documents and introduces an AI-supported summary workflow while maintaining access control and deployment realism.

## Target users

- regular employee who uploads and reviews own documents
- administrator who manages visibility, diagnostics, and platform settings
- evaluator or professor who needs a low-friction demo and verification path

## MVP definition

The minimum acceptable product includes:

- user registration and login
- role-aware access control
- PDF upload
- document metadata storage
- AI summary generation for one uploaded document
- simple question-answer flow over one document
- OpenAPI documentation
- Docker-based startup path
- deployment path for a VPS

## Out of scope for the first milestone

- OCR for scanned files
- team workspaces
- document sharing between groups
- advanced retrieval pipeline with vector database
- real-time notifications
- full audit dashboard

## Constraints

- the project should avoid unnecessary paid services
- production should run on a personal VPS
- local startup should remain simple for the evaluator
- documentation must be rich and updated after every phase

## Deliverables from this phase

- clear project topic
- user and feature scope
- MVP boundary
- alignment with course requirements

## Verification

- scenario supports a real multi-user environment
- scenario includes cloud-style integrations
- scenario is complex enough for security and cost analysis

## Next step

Translate the scope into architecture, infrastructure, and repository scaffolding.
