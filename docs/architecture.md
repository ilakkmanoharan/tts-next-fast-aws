# Architecture Diagram

```mermaid
flowchart TD
    A[Frontend: Next.js] -->|POST /generate-audio| B[FastAPI Backend (ECS Fargate)]
    B -->|Polly Synthesize| C[AWS Polly]
    B -->|Upload| D[S3 Bucket]
    D -->|Presigned URL| A
    B -->|GET /voices| C
