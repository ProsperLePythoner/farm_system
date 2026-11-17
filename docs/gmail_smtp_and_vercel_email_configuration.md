# Farm System — Gmail SMTP & Vercel Email Configuration

This guide explains how to configure Gmail as the email-sending service for **farm_system**, test email delivery locally, and configure the necessary environment variables on Vercel.

## 1. Create a Dedicated Sending Account

Create a new Gmail account exclusively for the application.

For example:

`yourfarm.alerts@gmail.com`

**Why use a dedicated account?**

- Avoid using your personal Gmail account.
- The application will use an App Password capable of sending emails through this account.
- If the credentials are ever compromised, the dedicated account limits potential exposure.
- Keeps application notifications separate from personal correspondence.

Ideally, this account should contain no personal information or unrelated correspondence.

## 2. Enable 2-Step Verification and Generate an App Password

1. Sign in to your dedicated Gmail account.
2. Visit [Google Account Security](https://myaccount.google.com/security).
3. Enable **2-Step Verification**.
4. Once enabled, visit [Google App Passwords](https://myaccount.google.com/apppasswords).
5. Generate a new App Password and name it `farm_system`.
6. Copy the generated 16-character password.

**Important:**
- Google requires 2-Step Verification before allowing App Password generation.
- The App Password is different from your normal Gmail password.
- Google displays the generated password only once.
- Remove any spaces before using it in your environment variables.
- Never commit this password to GitHub or expose it in source code.

## 3. Test Email Delivery Locally Before Configuring Vercel

Before modifying your production environment, verify that Gmail SMTP works correctly on your local machine.

Open PowerShell in your Django project directory and set the following environment variables.

### 3.1 Configure temporary environment variables

These variables apply only to the current PowerShell session.

```powershell
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "true"
$env:EMAIL_HOST_USER = "yourfarm.alerts@gmail.com"
$env:EMAIL_HOST_PASSWORD = "<the 16 characters, no spaces>"
$env:DEFAULT_FROM_EMAIL = "Farm System <yourfarm.alerts@gmail.com>"
```

Replace the placeholder values with your actual Gmail address and App Password.

**Never share your actual credentials in public repositories, screenshots, or conversations.**

### 3.2 Send a test email

Execute the following command:

```powershell
python manage.py shell -c "from django.core.mail import send_mail; print(send_mail('farm_system test', 'It works.', None, ['your-own-address@gmail.com']))"
```

Replace `your-own-address@gmail.com` with an inbox you can access.

**Expected result:**

- The terminal should print `1`, indicating that Django's email backend accepted the message.
- The email should arrive in the recipient's inbox, ideally within a minute.

Note that `None` tells Django to use `DEFAULT_FROM_EMAIL` as the sender.

This also verifies that Django is loading the expected default sender configuration.

**Important:** A return value of `1` does not guarantee final delivery. Check the recipient's Spam folder if the email doesn't appear in the inbox.

### 3.3 Clean up the temporary environment variables

After testing, remove the credentials from your current PowerShell session.

```powershell
Remove-Item Env:EMAIL_HOST, Env:EMAIL_PORT, Env:EMAIL_USE_TLS, Env:EMAIL_HOST_USER, Env:EMAIL_HOST_PASSWORD, Env:DEFAULT_FROM_EMAIL
```

This prevents the credentials from lingering in the current terminal session.

### 3.4 Troubleshooting common SMTP errors

| Error | Meaning | Possible solution |
|---|---|---|
| `534 ... Application-specific password required` | Gmail requires an App Password, but a normal password was supplied. | Enable 2-Step Verification and generate an App Password. |
| `535 ... Username and Password not accepted` | The credentials are incorrect, revoked, or improperly formatted. | Verify the Gmail address and App Password. Ensure spaces have been removed. |
| Timeout or connection error | The SMTP connection could not be established. | Check your internet connection and whether port 587 is blocked by your network. Try another network if necessary. |

## 4. Configure Environment Variables in Vercel

Once local email delivery works, configure the production environment.

1. Open your project in the [Vercel Dashboard](https://vercel.com/dashboard).
2. Navigate to **Settings → Environment Variables**.
3. Add the following variables.
4. Select **Production** as the target environment.

### 4.1 Required environment variables

| Variable | Value | Sensitive? |
|---|---|---|
| `EMAIL_HOST` | `smtp.gmail.com` | No |
| `EMAIL_PORT` | `587` | No |
| `EMAIL_USE_TLS` | `true` | No |
| `EMAIL_HOST_USER` | Your dedicated sending Gmail address | Yes |
| `EMAIL_HOST_PASSWORD` | Your Gmail App Password | Yes |
| `DEFAULT_FROM_EMAIL` | `Farm System <yourfarm.alerts@gmail.com>` | No |
| `DJANGO_SITE_URL` | Your live application URL, e.g. `https://yourdomain.example` | No |
| `CRON_SECRET` | A long, randomly generated secret | Yes |

Replace all example values with the actual production values.

For sensitive variables, enable Vercel's **Sensitive** option where available.

### 4.2 Generate a secure CRON_SECRET

Use Python's `secrets` module to generate a cryptographically secure random value.

Run this command in PowerShell:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into Vercel's `CRON_SECRET` environment variable.

Do not expose this value publicly or commit it to GitHub.

### 4.3 Important Gmail sender configuration

Ensure that:

- `EMAIL_HOST_USER` contains your dedicated Gmail address.
- `DEFAULT_FROM_EMAIL` uses that same Gmail address.

For example:

```text
EMAIL_HOST_USER = yourfarm.alerts@gmail.com
DEFAULT_FROM_EMAIL = Farm System <yourfarm.alerts@gmail.com>
```

Gmail generally uses the authenticated account as the sending identity. Using a different sender address can result in Gmail replacing the specified From address or creating sender-authentication issues.

## 5. Redeploy the Application

**Environment variable changes do not automatically update an existing deployment.**

After saving your environment variables:

1. Open your Vercel project's **Deployments** section.
2. Locate the latest production deployment.
3. Trigger a new deployment (redeploy).
4. Wait for the deployment to complete successfully.
5. Test the application's automatic email notifications.

Verify that the deployment is using the correct Production environment variables.

---

## 6. Final Verification Checklist

Use this checklist to confirm that the email configuration is complete.

- [x] Dedicated Gmail sending account created.
- [x] 2-Step Verification enabled.
- [x] Gmail App Password generated.
- [x] App Password tested locally.
- [x] Test email successfully received.
- [x] Temporary local environment variables cleaned up.
- [ ] All required Vercel environment variables configured.
- [ ] Sensitive variables protected.
- [ ] `DJANGO_SITE_URL` points to the live application.
- [ ] `CRON_SECRET` generated and configured.
- [ ] Production deployment redeployed successfully.
- [ ] Automatic farm_system email notifications tested.

**Configuration complete:** Gmail SMTP is ready to serve as the email delivery mechanism for farm_system, subject to successful production verification.