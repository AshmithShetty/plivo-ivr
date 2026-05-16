# Plivo IVR App

### Demo Link - https://plivo-ivr-652c.onrender.com


## Setup Instructions

1. Create and activate a virtual environment.

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install the dependencies.

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root.

You can use `env.example` as the reference.

## Required Plivo Credentials

Add these values to your `.env` file:

```env
PLIVO_AUTH_ID=your_auth_id
PLIVO_AUTH_TOKEN=your_auth_token
PLIVO_NUMBER=your_plivo_phone_number
ASSOCIATE_NUMBER=02264236412
BASE_URL=http://localhost:5000
```

Required Plivo credentials:
- `PLIVO_AUTH_ID`
- `PLIVO_AUTH_TOKEN`

## Steps To Run And Test

1. Start the app.

```powershell
python app.py
```

2. Open this URL in your browser:

```text
http://localhost:5000
```

3. Enter a phone number in the form and submit it.

4. Test the IVR flow on the call:
- Enter the OTP
- Choose a language
- Choose to play audio or connect to the associate
