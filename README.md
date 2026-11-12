# Brightwell Home Cleaning website

*"Brightwell Home Cleaning" is a placeholder name until the business confirms its own.*

A new website for a home cleaning business. Customers can browse services and see what each visit covers. The goal is an online store where they choose a service, pick a date and time, and book and pay online.

## What works today

- **Home page** in the same structure as the reference site: a services menu, an introduction, the services, why customers choose us, who we are, how booking works, and contact details.
- **Service pages** for five starter services: standard clean, deep clean, move-in or move-out clean, post-renovation clean, and upholstery refresh. Each one has a checklist of what the visit covers.
- **Owner administration** at `/admin/`. The owner adds or edits services, sets prices and visit lengths, hides a service, and changes the order services appear in.
- **Staff sign-in** with secure passwords. Customer accounts come later.

Until online booking is ready, every "book" action points to the phone number and email address. The site never shows a booking button that doesn't work.

## What the owner needs to confirm

- Business name, phone, email, service area, and opening hours (all placeholders today).
- Prices for each service. Until a price is set, the site shows "Price on request".
- The wording of each service and of the "Why customers choose us" and "Who we are" sections, which are drafts.
- Photos: the site uses free stock photos from Unsplash for now (credits in `static/img/CREDITS.md`). The business's own photos can replace them.

## Next steps

1. Online booking: choose a date and time from available slots, with no double bookings.
2. Customer accounts and email confirmations.
3. Online payment at checkout.
4. Publishing the site on the internet (free hosting options are available to start).

## Costs

Everything so far uses free software and runs on a local computer. Running it on the internet can start on free plans; payment processing charges a fee per transaction.

Technical documentation (setup, configuration, tests): [docs/DEVELOPER.md](docs/DEVELOPER.md).
