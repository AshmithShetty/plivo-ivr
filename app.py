import os
from flask import Flask, request, render_template, jsonify
from flask import Response as FlaskResponse
import plivo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load credentials from .env
AUTH_ID          = os.getenv("PLIVO_AUTH_ID")
AUTH_TOKEN       = os.getenv("PLIVO_AUTH_TOKEN")
PLIVO_NUMBER     = os.getenv("PLIVO_NUMBER")
BASE_URL         = os.getenv("BASE_URL", "http://localhost:5000")
OTP              = os.getenv("OTP")

# Associate number: 02264236412 
ASSOCIATE_NUMBER = os.getenv("ASSOCIATE_NUMBER", "02264236412")

# Credential check
_required = {
    "PLIVO_AUTH_ID":    AUTH_ID,
    "PLIVO_AUTH_TOKEN": AUTH_TOKEN,
    "PLIVO_NUMBER":     PLIVO_NUMBER,
    "OTP":              OTP,
}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Copy .env.example to .env and fill in the values."
    )

client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

#Helper
def xml_resp(el):
    """Return a Plivo XML response with the correct content-type."""
    return FlaskResponse(el.to_string(), mimetype="text/xml")



# Health Check for render


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200




@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/make-call", methods=["POST"])
def make_call():
    to_number = request.form.get("phone", "").strip()

    # Normalising to Indian number
    if not to_number.startswith("+"):
        if to_number.startswith("91") and len(to_number) == 12:
            to_number = "+" + to_number
        else:
            to_number = "+91" + to_number

    try:
        resp = client.calls.create(
            from_=PLIVO_NUMBER,
            to_=to_number,
            answer_url=f"{BASE_URL}/answer",
            answer_method="POST"
        )
        return render_template(
            "index.html",
            status="success",
            message=f"Call initiated! Request UUID: {resp['request_uuid']}"
        )
    except Exception as e:
        return render_template(
            "index.html",
            status="error",
            message=f"Error: {str(e)}"
        )


# OTP Authentication

@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Called by Plivo when callee picks up. Prompts for 4-digit OTP."""
    r = plivo.plivoxml.ResponseElement()

    gd = plivo.plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/otp",
        method="POST",
        numDigits=4,
        timeout=10,
        retries=5
    )
    gd.add(plivo.plivoxml.SpeakElement(
        "Welcome to InspireWorks. "
        "Please enter your 4-digit O T P to continue.",
        loop=1
    ))
    r.add(gd)
    # Fallback: caller timed out 
    r.add(plivo.plivoxml.RedirectElement(f"{BASE_URL}/answer", method="POST"))
    return xml_resp(r)


@app.route("/otp", methods=["GET", "POST"])
def otp():
    """Validates the OTP. Re-prompts on wrong entry."""
    digits = request.form.get("Digits", "").strip()
    r = plivo.plivoxml.ResponseElement()

    if digits == OTP:
        r.add(plivo.plivoxml.SpeakElement(
            "Authentication successful. Welcome to InspireWorks!"
        ))
        r.add(plivo.plivoxml.RedirectElement(f"{BASE_URL}/ivr-level1", method="POST"))
    else:
        r.add(plivo.plivoxml.SpeakElement(
            "Incorrect O T P. Please try again."
        ))
        r.add(plivo.plivoxml.RedirectElement(f"{BASE_URL}/answer", method="POST"))

    return xml_resp(r)


# Level 1 IVR Menu

@app.route("/ivr-level1", methods=["GET", "POST"])
def ivr_level1():
    """Language selection menu."""
    r = plivo.plivoxml.ResponseElement()

    gd = plivo.plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/ivr-level2",
        method="POST",
        numDigits=1,
        timeout=10,
        retries=3
    )
    gd.add(plivo.plivoxml.SpeakElement(
        "Please select your language. "
        "Press 1 for English. "
        "Press 2 for Spanish.",
        loop=2
    ))
    r.add(gd)
    # Fallback: no input
    r.add(plivo.plivoxml.RedirectElement(f"{BASE_URL}/ivr-level1", method="POST"))
    return xml_resp(r)


# Level 2 IVR
@app.route("/ivr-level2", methods=["GET", "POST"])
def ivr_level2():
    """Reads language digit, then presents the action menu."""
    lang_digit = request.form.get("Digits", "").strip()
    r = plivo.plivoxml.ResponseElement()

    if lang_digit == "1":
        lang, lang_name = "en", "English"
    elif lang_digit == "2":
        lang, lang_name = "es", "Spanish"
    else:
        # Go back to level 1 if invalid language input
        r.add(plivo.plivoxml.SpeakElement("Invalid selection. Please try again."))
        r.add(plivo.plivoxml.RedirectElement(f"{BASE_URL}/ivr-level1", method="POST"))
        return xml_resp(r)

    gd = plivo.plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/ivr-action?lang={lang}",
        method="POST",
        numDigits=1,
        timeout=10,
        retries=3
    )
    gd.add(plivo.plivoxml.SpeakElement(
        f"You have selected {lang_name}. "
        "Press 1 to play an audio message. "
        "Press 2 to connect to a live associate.",
        loop=2
    ))
    r.add(gd)
    # Fallback: no input 
    r.add(plivo.plivoxml.RedirectElement(
        f"{BASE_URL}/ivr-level2-retry?lang={lang}", method="POST"
    ))
    return xml_resp(r)


@app.route("/ivr-level2-retry", methods=["GET", "POST"])
def ivr_level2_retry():
    """Re-shows Level 2 action menu (used on timeout, without re-reading language)."""
    lang = request.args.get("lang", "en")
    lang_name = "English" if lang == "en" else "Spanish"

    r = plivo.plivoxml.ResponseElement()
    gd = plivo.plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/ivr-action?lang={lang}",
        method="POST",
        numDigits=1,
        timeout=10,
        retries=3
    )
    gd.add(plivo.plivoxml.SpeakElement(
        f"You have selected {lang_name}. "
        "Press 1 to play an audio message. "
        "Press 2 to connect to a live associate.",
        loop=2
    ))
    r.add(gd)
    r.add(plivo.plivoxml.RedirectElement(
        f"{BASE_URL}/ivr-level2-retry?lang={lang}", method="POST"
    ))
    return xml_resp(r)


# Level 2 Logic

@app.route("/ivr-action", methods=["GET", "POST"])
def ivr_action():
    """
    1 → Play a MP3
    2 → Dial live associate at 02264236412
    """
    digit = request.form.get("Digits", "").strip()
    lang  = request.args.get("lang", "en")
    r = plivo.plivoxml.ResponseElement()

    if digit == "1":
        # Play audio message
        r.add(plivo.plivoxml.SpeakElement(
            "Playing a short audio message."
        ))
        r.add(plivo.plivoxml.PlayElement(
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        ))
        r.add(plivo.plivoxml.SpeakElement("Thank you for listening. Goodbye!"))
        r.add(plivo.plivoxml.HangupElement())

    elif digit == "2":
        
        r.add(plivo.plivoxml.SpeakElement(
            "Connecting you to a live associate. Please hold."
        ))
        dial = plivo.plivoxml.DialElement()
        dial.add(plivo.plivoxml.NumberElement(ASSOCIATE_NUMBER))
        r.add(dial)
        r.add(plivo.plivoxml.SpeakElement(
            "We are sorry, all associates are currently busy. Please contact later"
        ))
        r.add(plivo.plivoxml.HangupElement())

    else:
        # Invalid input - reprompt
        r.add(plivo.plivoxml.SpeakElement("Invalid selection. Please try again."))
        r.add(plivo.plivoxml.RedirectElement(
            f"{BASE_URL}/ivr-level2-retry?lang={lang}", method="POST"
        ))

    return xml_resp(r)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
