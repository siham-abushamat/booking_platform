# Booking Management System

A Python desktop app for managing bookings at a venue that offers services such as a tennis court, a meeting room and a spa. Staff can manage customers, available dates and time slots, and bookings, and view reports on bookings and revenue. The interface is built with Tkinter and the data is stored in a SQLite database.

![Welcome screen image](welcome.png)

## Features

- **Customers:** add, edit and delete customer records (name, email, phone).
- **Available dates and services:** manage each service's date, time slot and price.
- **Bookings:** choose a customer and a time slot from drop-down lists and enter the number of guests. The total price is calculated automatically (guests × price).
- **Related records:** see all bookings for a customer or a service, or the customer and service behind a booking.
- **Input checks:**
  - Required fields, a valid email address, dates in `YYYY-MM-DD` format, no negative prices and at least one guest.
  - A customer or time slot that still has bookings can't be deleted.
- **Import and export:** export any table to CSV or Excel, or import records from CSV or Excel. Imports are checked first: if any row is invalid, nothing is saved.
- **Reports:**
  - Total bookings, total revenue and average booking value.
  - A bar chart of bookings per service.
  - The most-booked services and the 10 highest-value bookings.

## Database

The app uses three related tables in `bookings.db`:

| Table | Columns | Notes |
|---|---|---|
| `users` | `user_id`, `name`, `email`, `phone` | Email must be unique |
| `available_dates` | `date_id`, `service_name`, `booking_date`, `time_slot`, `price` | Price can't be negative |
| `bookings` | `booking_id`, `user_id`, `date_id`, `guests`, `total_price` | `user_id` → `users`, `date_id` → `available_dates`; guests must be more than 0 |

Foreign keys are switched on, so every booking must point to an existing customer and time slot. If `bookings.db` doesn't exist, the app creates it on first run with sample data: 3 customers, plus 3 services (Tennis Court, Meeting Room and Spa Session).

## Built with

- Python 3
- Tkinter (interface)
- SQLite (database)
- pandas (CSV and Excel import and export, reports)
- Matplotlib (charts)
- Pillow (welcome screen image)
- openpyxl (Excel files)

## How to run

1. Install Python 3 from [python.org](https://www.python.org/downloads/), which includes Tkinter.
2. Install the packages:
   ```
   pip install pandas matplotlib pillow openpyxl
   ```
3. In the project folder, run:
   ```
   python dhp.py
   ```
   On a Mac, use `python3 dhp.py`.
4. Click **ENTER** on the welcome screen. The main menu opens with four sections: Customers, Available Dates & Services, Bookings and Reports.

## Importing data

An import file must have exactly the same columns, in the same order, as the table it goes into:

- **Customers:** `user_id, name, email, phone`
- **Available dates:** `date_id, service_name, booking_date, time_slot, price`
- **Bookings:** `booking_id, user_id, date_id, guests, total_price`

Leave the ID column empty and the app will number new records automatically.

## Project structure

```
booking_platform/
├── dhp.py        # The app: database setup, screens, import/export and reports
├── welcome.png   # Background image for the welcome screen
└── bookings.db   # SQLite database (created automatically on first run)
```
