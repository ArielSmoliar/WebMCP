# Deploy to Google Cloud

Captain's Table runs on Cloud Run and stores production workflow state in
Firestore Native mode. Local development continues to use SQLite by default.

## Production contract

- Cloud Run service: `captains-table-webmcp`
- Region: `us-east1`
- Firestore database: `captains-table`, Native mode
- Firestore collection: `captains_table_sessions`
- Runtime service account: `captains-table-webmcp`
- Public HTTPS ingress; unauthenticated access is required for judges and WebMCP
- Chrome WebMCP Origin Trial registration for the production origin expires
  November 16, 2026; renew or remove the token in `static/index.html` before
  that date

The runtime service account receives `roles/datastore.user` through an IAM
condition that matches only the `captains-table` database. Cloud Run supplies
Application Default Credentials; do not add a service-account key or set
`GOOGLE_APPLICATION_CREDENTIALS`.

## One-time project setup

```bash
PROJECT_ID="your-project-id"
REGION="us-east1"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com firestore.googleapis.com \
  --project "$PROJECT_ID"

gcloud firestore databases create \
  --database="captains-table" \
  --location="$REGION" \
  --type=firestore-native \
  --delete-protection \
  --project "$PROJECT_ID"

gcloud iam service-accounts create captains-table-webmcp \
  --display-name="Captain's Table WebMCP" \
  --project "$PROJECT_ID"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:captains-table-webmcp@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition="expression=resource.name==\"projects/${PROJECT_ID}/databases/captains-table\",title=CaptainTableDatabaseOnly,description=Restrict runtime access to the Captain Table database"
```

If the named database already exists, describe it rather than creating it again:

```bash
gcloud firestore databases describe --database="captains-table" --project "$PROJECT_ID"
```

## Deploy

```bash
gcloud run deploy captains-table-webmcp \
  --source=. \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --service-account="captains-table-webmcp@${PROJECT_ID}.iam.gserviceaccount.com" \
  --set-env-vars="CAPTAINS_TABLE_STORAGE=firestore,CAPTAINS_TABLE_FIRESTORE_DATABASE=captains-table" \
  --allow-unauthenticated \
  --min=0 \
  --max=3
```

## Verify

```bash
SERVICE_URL="$(gcloud run services describe captains-table-webmcp \
  --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')"

curl --fail-with-body "$SERVICE_URL/health"
curl --fail-with-body "$SERVICE_URL/readyz"
```

Create and mutate a session, deploy a new revision, then fetch the same session
to demonstrate that the authorization record and receipt survive application
replacement.
