from django.conf import settings
import PyPDF2
from django.http import JsonResponse
from docx import Document
def parsedResume(file):
    filename=file.name.lower()
    if filename.endswith(".pdf"):
        return parsingResume(file)
    elif filename.endswith('.docx'):
        return parsingDocx(file)
    else:
        raise ValueError("Unsupported file format")
    

def parsingResume(file):
    reader=PyPDF2.PdfReader(file)
    text=""
    for page in reader.pages:
        text+=page.extract_text() or ""
    return text


def parsingDocx(file):
    doc=Document(file)
    para=""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return para


import resend


resend.api_key = settings.RESEND_API_KEY

def send_welcome_email(user):
    try:
        resend.Emails.send({
            "from": "ResumeTC <onboarding@resend.dev>",
            "to": user.email,
            "subject": "You're in! Welcome to ResumeTC",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;max-width:600px;width:100%;">
        
        <!-- Header -->
        <tr>
          <td style="background:#1a1a2e;padding:32px 40px;text-align:center;">
            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;letter-spacing:-0.5px;">ResumeTC</h1>
            <p style="margin:8px 0 0;color:#a0a0b8;font-size:14px;">AI-Powered Resume Analyzer</p>
          </td>
        </tr>

        <!-- Hero -->
        <tr>
          <td style="padding:40px 40px 24px;">
            <h2 style="margin:0 0 12px;font-size:28px;font-weight:700;color:#1a1a2e;line-height:1.3;">Hey {user.username}, you're officially in! </h2>
            <p style="margin:0;font-size:16px;color:#555;line-height:1.7;">Welcome to <strong>ResumeTC</strong> — the smartest way to get your resume noticed by recruiters and ATS systems.</p>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

        <!-- Features -->
        <tr>
          <td style="padding:28px 40px;">
            <p style="margin:0 0 20px;font-size:15px;font-weight:600;color:#1a1a2e;">Here's what you can do right now:</p>
            
            <table cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td style="padding:12px 0;border-bottom:1px solid #f5f5f5;">
                  <table cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="width:36px;height:36px;background:#eef2ff;border-radius:8px;text-align:center;vertical-align:middle;font-size:18px;">📄</td>
                      <td style="padding-left:14px;">
                        <p style="margin:0;font-size:15px;font-weight:600;color:#1a1a2e;">Upload your resume</p>
                        <p style="margin:2px 0 0;font-size:13px;color:#888;">PDF or Word — we handle both</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td style="padding:12px 0;border-bottom:1px solid #f5f5f5;">
                  <table cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="width:36px;height:36px;background:#f0fdf4;border-radius:8px;text-align:center;vertical-align:middle;font-size:18px;">🎯</td>
                      <td style="padding-left:14px;">
                        <p style="margin:0;font-size:15px;font-weight:600;color:#1a1a2e;">Get your ATS score</p>
                        <p style="margin:2px 0 0;font-size:13px;color:#888;">See exactly how recruiters see you</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td style="padding:12px 0;">
                  <table cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="width:36px;height:36px;background:#fff7ed;border-radius:8px;text-align:center;vertical-align:middle;font-size:18px;">🚀</td>
                      <td style="padding-left:14px;">
                        <p style="margin:0;font-size:15px;font-weight:600;color:#1a1a2e;">Get AI suggestions</p>
                        <p style="margin:2px 0 0;font-size:13px;color:#888;">Improve your resume with one click</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- CTA -->
        <tr>
          <td style="padding:8px 40px 40px;text-align:center;">
            <a href="https://ResumeTC-orn7.onrender.com" style="display:inline-block;background:#1a1a2e;color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;padding:14px 36px;border-radius:8px;letter-spacing:0.2px;">Analyze my resume now</a>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px;text-align:center;">
            <p style="margin:0;font-size:13px;color:#aaa;line-height:1.6;">You're receiving this because you signed up at ResumeTC.<br>Questions? Just reply to this email — we read every one.</p>
            <p style="margin:12px 0 0;font-size:13px;color:#aaa;">— Team ResumeTC</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
""",
        })
    except Exception as e:
        print(f"Welcome email failed: {e}")


def send_purchase_email(user):
    try:
        resend.Emails.send({
            "from": "ResumeTC <onboarding@resend.dev>",
            "to": user.email,
            "subject": f"Payment confirmed — {user.profile.plan} plan is active!",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;max-width:600px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:#1a1a2e;padding:32px 40px;text-align:center;">
            <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;letter-spacing:-0.5px;">ResumeTC</h1>
            <p style="margin:8px 0 0;color:#a0a0b8;font-size:14px;">AI-Powered Resume Analyzer</p>
          </td>
        </tr>

        <!-- Hero -->
        <tr>
          <td style="padding:40px 40px 24px;">
            <h2 style="margin:0 0 12px;font-size:28px;font-weight:700;color:#1a1a2e;">Payment confirmed!</h2>
            <p style="margin:0;font-size:16px;color:#555;line-height:1.7;">Hey {user.username}, your <strong>{user.profile.plan} plan</strong> is now active. Time to get to work!</p>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

        <!-- Plan details -->
        <tr>
          <td style="padding:28px 40px;">
            <p style="margin:0 0 16px;font-size:15px;font-weight:600;color:#1a1a2e;">Your plan details:</p>
            <table cellpadding="0" cellspacing="0" width="100%" style="background:#f8f9ff;border-radius:8px;border:1px solid #e8eaf6;">
              <tr>
                <td style="padding:16px 20px;border-bottom:1px solid #e8eaf6;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="font-size:14px;color:#888;">Plan</td>
                      <td style="text-align:right;font-size:14px;font-weight:600;color:#1a1a2e;">{user.profile.plan}</td>
                    </tr>
                  </table>
                </td>
              </tr>
              <tr>
                <td style="padding:16px 20px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="font-size:14px;color:#888;">Credits available</td>
                      <td style="text-align:right;font-size:14px;font-weight:600;color:#1a1a2e;">{user.profile.credits}</td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- CTA -->
        <tr>
          <td style="padding:8px 40px 40px;text-align:center;">
            <a href="https://ResumeTC-orn7.onrender.com" style="display:inline-block;background:#1a1a2e;color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;padding:14px 36px;border-radius:8px;">Start analyzing now</a>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 40px;"><div style="height:1px;background:#f0f0f0;"></div></td></tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px;text-align:center;">
            <p style="margin:0;font-size:13px;color:#aaa;line-height:1.6;">Questions about your plan? Just reply — we're happy to help.</p>
            <p style="margin:12px 0 0;font-size:13px;color:#aaa;">— Team ResumeTC</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
""",
        })
    except Exception as e:
        print(f"Purchase email failed: {e}")

def custom_ratelimit_error(request, exception):
    return JsonResponse({
        "error": "Too many login attempts. Try again later."
    }, status=429)