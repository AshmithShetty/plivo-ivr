# Plivo IVR App

This project is a Flask-based Plivo IVR application. It places an outbound call, asks the callee to enter a 4-digit OTP, presents a language menu, and then either plays an audio file or connects the caller to a live associate.

## Demo Link

Demo Link - https://plivo-ivr-652c.onrender.com


## Setup Instructions

### 1. Clone the project and open it

```powershell
git clone https://github.com/AshmithShetty/plivo-ivr.git
cd plivo
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create the environment file

Create a `.env` file in the project root. You can copy from `env.example`.

Example:

```env
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token
PLIVO_NUMBER=918035736861
ASSOCIATE_NUMBER=02264236412
BASE_URL=https://your-render-service.onrender.com 
```

## Required Plivo Credentials

The application requires the following Plivo credentials:

- `PLIVO_AUTH_ID`
- `PLIVO_AUTH_TOKEN`

The following values are also required for the IVR flow to work correctly:

- `PLIVO_NUMBER`: your Plivo phone number used to place the outbound call
- `ASSOCIATE_NUMBER`: the destination number used when the caller selects the live associate option
- `BASE_URL`: the public base URL where this app is hosted

## Important Note About Local vs Full Testing

The application can be started locally, but the full IVR flow depends on Plivo calling back into the app on routes such as `/answer`, `/otp`, `/ivr-level1`, and `/ivr-action`.

Because of that, full end-to-end testing requires a public URL. For the judge to test complete functionality, this app should be deployed on Render and `BASE_URL` must be set to the Render service URL.

## Render Setup

Use Render for the final testable deployment so that Plivo can reach the application over the public internet.

### 1. Push the project to GitHub

Render deploys from a Git repository, so make sure this project is pushed to GitHub.

### 2. Create a new Web Service on Render

On Render:

1. Click `New +`
2. Select `Web Service`
3. Connect the GitHub repository
4. Choose the branch to deploy

### 3. Configure the Render service

Use the following settings:

- Environment: `Python 3`
- Build Command:

```text
pip install -r requirements.txt
```

- Start Command:

```text
python app.py
```

### 4. Add environment variables on Render

In the Render dashboard, add these environment variables:

```env
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token
PLIVO_NUMBER=918035736861
ASSOCIATE_NUMBER=02264236412
BASE_URL=https://your-render-service.onrender.com
```

`BASE_URL` must exactly match the public Render URL of the deployed app.

### 5. Deploy and verify

After deployment:

1. Open the Render URL in the browser
2. Confirm the home page loads
3. Confirm the health endpoint works:

```text
https://your-render-service.onrender.com/health
```

It should return:

```json
{"status":"ok"}
```

## Steps to Run and Test

For full testing, use the deployed Render URL.

### A. Optional local run

This is useful for basic UI verification only.

```powershell
python app.py
```

Open:

```text
http://localhost:5000
```

Note: local execution alone does not provide the full callback-based IVR experience unless the app is exposed through a public tunnel. The recommended judge setup is Render.

### B. Full end-to-end test on Render

1. Open the deployed Render URL in a browser.
2. Enter a destination phone number in the form.
3. Submit the form to initiate the outbound call.
4. Answer the incoming call.
5. Enter the OTP:

```text
2407
```

6. Choose a language:
- Press `1` for English
- Press `2` for Spanish

7. Choose an action:
- Press `1` to play the audio message
- Press `2` to connect to the live associate number

## Summary 

To test complete functionality:

1. Deploy the app on Render
2. Set valid Plivo credentials and phone numbers in Render environment variables
3. Set `BASE_URL` to the Render app URL
4. Open the Render app in the browser
5. Trigger a call and complete the IVR flow using OTP `2407`
