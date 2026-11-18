# Farm System — Automated Email Briefings

## 1. Overview

Farm System sends automated daily email briefings to eligible users, keeping them informed about important farm operations that may require attention.

Each briefing summarizes relevant harvest windows and outstanding customer payments, depending on the recipient's assigned role.

The system is designed to:
- Notify relevant personnel about approaching harvest windows.
- Highlight harvest windows that have ended without a harvest record.
- Remind responsible personnel about overdue customer payments.
- Provide a convenient link to the application dashboard.
- Deliver role-specific information while respecting access permissions.

---

## 2. Sample Email

The following is an example of the daily briefing sent to an eligible recipient.

**To:** `amina@example.test`

**Subject:** Farm briefing Tue 17 Nov: 2 harvest windows, 1 unrecorded, 1 payment due

### Email body

```text
Good morning, Amina.

Your farm briefing for Tuesday 17 November 2026:

HARVESTS

Harvest window open now
  - Tomatoes (Block A): 16 Nov – 18 Nov. 1 day left in window.

Opening within 3 days
  - Tomatoes (Block A): 19 Nov – 21 Nov. Window opens in 2 days.

Window ended and no harvest was recorded
  - Tomatoes (Block A): 07 Nov – 09 Nov.

PAYMENTS

Payments to collect (unpaid 7+ days)
  - Order #1, Mlimani Market (0700111222): TSh 10,000.00 outstanding, 10 days since order.

Open the dashboard: https://farm.example.com/dashboard/
```

---

## 3. Role-Based Email Distribution

Not every user receives the same briefing. The system determines which sections each recipient is authorized to receive based on their assigned role.

| Recipient | Assigned role | Email content |
|---|---|---|
| Amina | Administrator | HARVESTS + PAYMENTS |
| Juma | Harvest Manager | HARVESTS only |
| Neema | Sales Manager | PAYMENTS only |
| Sam | Staff | No email |
| User without an email address | Any role | No email |

### Recipient eligibility

An email is sent only to users who:
- Have an active account.
- Have a valid email address configured.
- Hold at least one qualifying role for the relevant notification section.

**Superusers:** Superusers receive all available notification sections, regardless of their assigned role.

**Users with no relevant information:** If a recipient has nothing requiring attention, no email is sent.

---

## 4. How Each Section Is Generated

### 4.1 Email recipients

The system considers active users with email addresses and qualifying roles.

Recipient permissions are evaluated separately for harvest and payment notifications.

### 4.2 Subject line

The subject contains the briefing date and counts for each section containing relevant information.

The counts represent:
- **Harvest windows:** Windows currently open plus those opening within the configured lead period.
- **Unrecorded:** Windows that have ended without a corresponding harvest record.
- **Payments due:** Orders with outstanding balances that have reached the configured reminder age.

Sections without relevant information are excluded from the subject.

### 4.3 Harvest notifications

Harvest notifications are divided into three categories.

#### A. Harvest window open now

A planting appears here when today's date falls within its calculated harvest window.

The calculation is:

```text
Window start = Planting date + Crop maturity days
Window end   = Window start + 2 days
```

Both the start and end dates are inclusive.

#### B. Opening within 3 days

A planting appears here when its harvest window starts within the next 1–3 days.

The lead period is configurable through the `HARVEST_REMINDER_LEAD_DAYS` environment variable.

#### C. Window ended and no harvest was recorded

A planting appears here when:
- Its harvest window has already ended.
- The window ended within the previous 30 days.
- No harvest records are associated with that planting.

**Important wording distinction:** The system can only establish that no harvest was recorded in the database. It cannot establish that harvesting physically did not happen.

Consequently, the notification deliberately says *"Window ended and no harvest was recorded"* rather than claiming that the crop was never harvested.

### 4.4 Payment notifications

The payment section identifies orders that:
- Still have an outstanding balance.
- Were placed at least 7 days ago.

Orders are listed from oldest to newest.

Each entry includes:
- Order number.
- Customer name.
- Customer phone number.
- Outstanding amount.
- Number of days since the order was placed.

**Display limit:** A maximum of 10 payment entries are included. If additional orders qualify, the email displays an `...and N more` indicator.

---

## 5. Scheduling and Delivery

| Property | Configuration |
|---|---|
| Frequency | Once daily |
| Scheduled time | 04:00 UTC |
| East African Time | 07:00 EAT |
| Scheduler | Vercel Cron |
| Delivery method | Gmail SMTP |
| Email format | Plain text |

### Delivery behaviour

Vercel Cron triggers the notification endpoint according to its configured schedule.

The endpoint executes the Django notification logic, which:
1. Identifies eligible recipients.
2. Evaluates relevant harvest and payment conditions.
3. Generates recipient-specific email content.
4. Sends the resulting messages through Gmail SMTP.

The scheduled execution is expected within the configured hour; actual email delivery can take additional time.

### Email format

All briefings are plain-text emails.

They contain:
- No embedded images.
- No tracking pixels.
- No email-open tracking.

---

## 6. Privacy and Information Security

The payment section contains potentially sensitive customer information, including:
- Customer names.
- Phone numbers.
- Outstanding payment amounts.
- Associated order information.

For this reason, payment notifications are restricted to:

- Administrator
- Farm Manager
- Sales Manager

Harvest notifications follow their own role-based permissions.

**Privacy consideration:** Once an email has been delivered, its contents are stored in the recipient's email account and may remain accessible even after their Farm System account permissions change.

Recipients should therefore protect their email accounts and avoid forwarding these briefings to unauthorized individuals.

---

## 7. Customizing Email Behaviour

Several aspects of the notification system can be adjusted without redesigning its underlying architecture.

### 7.1 Configuration reference

| Desired change | Configuration | Location |
|---|---|---|
| Warn earlier or later about harvest windows | `HARVEST_REMINDER_LEAD_DAYS` | Environment variable (default: `3`) |
| Chase unpaid orders sooner or later | `PAYMENT_REMINDER_AFTER_DAYS` | Environment variable (default: `7`) |
| Change the email sending time | Cron schedule | `vercel.json` |
| Skip Sundays | Cron schedule | `vercel.json` |
| Change the sender name | `DEFAULT_FROM_EMAIL` | Environment variable |
| Change who receives each section | `HARVEST_RECIPIENT_ROLES`, `PAYMENT_RECIPIENT_ROLES` | Top of `reminders.py` |
| Change the payment entry limit | `PAYMENT_LIST_LIMIT` | `reminders.py` |
| Change how far back unrecorded harvests are considered | `MISSED_LOOKBACK_DAYS` | `services.py` |
| Change email wording or layout | `_harvest_lines`, `_payment_lines`, `build_digests` | `reminders.py` |

**Note:** Changing `MISSED_LOOKBACK_DAYS` also affects the dashboard's corresponding unrecorded-harvest information.

### 7.2 Changing the scheduled time

Cron schedules use UTC.

Examples:

| Desired schedule (EAT) | Cron expression (UTC) |
|---|---|
| 06:00 daily | `0 3 * * *` |
| 07:00 daily | `0 4 * * *` |
| 08:00 daily | `0 5 * * *` |

To skip Sundays, use:

```text
0 4 * * 1-6
```

This schedules execution Monday through Saturday at 07:00 EAT.

---

## 8. Testing Changes Safely

Before allowing modified notification behaviour to affect real recipients, test the changes using Django's management command.

### 8.1 Dry-run testing

Run:

```powershell
python manage.py send_reminders --dry-run
```

This allows you to inspect the notification results without sending the actual emails.

### 8.2 Testing a specific date

You can also simulate a different date:

```powershell
python manage.py send_reminders --dry-run --date 2026-11-24
```

This is particularly useful for checking how harvest windows and payment reminders behave on different dates.

**Recommendation:** Always test changes to notification rules using `--dry-run` before deploying them to production.

---

## 9. Current Limitations and Future Improvements

The current implementation uses centrally defined notification rules. Individual users cannot yet customize their own notification preferences.

The following features are not currently available:

| Feature | Current status |
|---|---|
| Individual notification opt-out | Not implemented |
| Choosing preferred notification sections | Not implemented |
| Per-user reminder schedules | Not implemented |
| Individual notification frequency | Not implemented |

### Potential future enhancement: Personal Notification Preferences

These features could be introduced through a dedicated database model linked to each user account.

For example, users could eventually:
- Disable email notifications.
- Choose whether to receive harvest alerts.
- Choose whether to receive payment reminders, subject to their role permissions.
- Customize notification preferences independently of other users.

This enhancement has deliberately been postponed to avoid introducing unnecessary database complexity before the core notification system is established.

---

## 10. Summary

Farm System's automated email briefing system provides a scheduled, role-aware communication mechanism for important farm operations.

Its primary responsibilities are:

1. **Harvest monitoring:** Identifies upcoming, currently open, and unrecorded harvest windows.
2. **Payment monitoring:** Identifies outstanding customer balances that have reached the reminder threshold.
3. **Role-based distribution:** Ensures recipients receive only the notification sections relevant to their permissions.
4. **Automated delivery:** Uses Vercel Cron and Gmail SMTP to deliver daily briefings.
5. **Configurable behaviour:** Allows administrators and developers to adjust notification rules and schedules.
6. **Privacy-conscious communication:** Restricts sensitive payment information to authorized management roles.

The system provides a foundation for expanding Farm System into a more proactive farm management platform, where relevant personnel are informed about important operational developments without needing to constantly monitor the dashboard.