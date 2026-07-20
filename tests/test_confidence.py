import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app
from backend.utils.confidence import get_confidence_label

app.testing = True

test_messages = [
    "WINNER!! You have been selected to receive a $1000 cash prize. Claim NOW by calling 09061701461!",
    "URGENT! Your mobile number has won £2000 in our lucky draw. Text CLAIM to 87121 now!",
    "FREE entry into our £250 weekly competition just text WIN to 80086 now. 18+ only.",
    "Congratulations! You've been selected for a FREE iPhone 15. Click here to claim: bit.ly/xyz123",
    "You have 1 new voicemail. Please call 09066362231 to hear it, calls cost 150p/min.",
    "Reminder: your account will be suspended. Verify your details immediately at the link below.",
    "Get cheap loans approved instantly, no credit check required! Apply now at loanfast.com",
    "Your parcel could not be delivered. Reschedule here: fake-delivery-tracking.com",
    "Last chance! 90% off all items today only. Shop now before it's gone!",
    "Hey are you free this weekend? Thinking of a movie night.",
    "Don't forget the team meeting tomorrow at 10am in conference room B.",
    "Can you send me the report before end of day please?",
    "Happy birthday! Hope you have an amazing day 🎉",
    "Mom, I'll be home late tonight, don't wait up for dinner.",
    "Your OTP for login is 483920. Do not share this with anyone.",
    "The plumber said he'll arrive around 3pm tomorrow to fix the sink.",
    "Let's catch up over coffee sometime next week?",
    "Reminder: dentist appointment on Thursday at 2:30pm.",
    "Thanks for helping me move last weekend, really appreciated it!",
    "See you at the gym tomorrow morning, same time as usual.",
]


def run_tests():
    client = app.test_client()
    passed = 0
    failed = 0

    for i, message in enumerate(test_messages, start=1):
        response = client.post('/predict', json={"message": message})
        data = response.get_json()

        if response.status_code != 200:
            print(f"[FAIL] Test {i}: API error - {data}")
            failed += 1
            continue

        returned_score = data["safety_score"]
        returned_label = data["confidence_label"]

        expected_label = get_confidence_label(returned_score)

        status = "PASS" if returned_label == expected_label else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"[{status}] Test {i:>2}  Score: {returned_score:>6}%  "
              f"Label: '{returned_label}'  |  Message: \"{message[:50]}...\"")

    print(f"\n{passed}/{len(test_messages)} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()