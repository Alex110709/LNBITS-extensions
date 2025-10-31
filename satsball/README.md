# SatsBall - LNbits Gambling Extension

SatsBall is a gambling extension for LNbits that allows users to place bets using Bitcoin Lightning payments. The extension features multiple "stacks" where users can place bets. Each stack accumulates Bitcoin, and there's a probability-based mechanism for users to win all the Bitcoin in a stack.

## Features

- Multiple betting stacks with independent accumulations
- Probability-based winning mechanism
- Admin configuration for each stack (winning probability, bet price, fee)
- Integration with satspay for Bitcoin payments
- Winner takes all accumulated Bitcoin in a stack

## Installation

1. Clone this repository to your LNbits extensions directory
2. Restart your LNbits server
3. Enable the SatsBall extension in the LNbits admin panel
4. Ensure the satspay extension is also enabled as it's a dependency

## Configuration

### Creating Stacks

As an admin, you can create multiple stacks with different configurations:

1. Navigate to the SatsBall admin panel
2. Click "Create New Stack"
3. Configure the stack parameters:
   - **Name**: Display name for the stack
   - **Description**: Detailed description of the stack
   - **Bet Price**: Fixed price for each bet in sats
   - **Winning Probability**: Chance of winning the stack (0.0-1.0)
   - **Fee Percentage**: Percentage of each bet taken as fee (0.0-100.0)
   - **Enabled**: Whether the stack is available for betting

### User Experience

1. Users visit the main SatsBall page to view available stacks
2. Users select a stack and place a bet
3. Users are redirected to a payment page via satspay
4. After payment, users have a chance to win all Bitcoin in the stack
5. Results are displayed immediately after payment confirmation

## Technical Details

### Data Models

#### Stack
- `id`: Unique identifier
- `name`: Display name
- `description`: Stack description
- `current_amount`: Accumulated amount in sats
- `bet_price`: Price per bet in sats
- `winning_probability`: Win probability (0.0-1.0)
- `fee_percentage`: House fee percentage
- `enabled`: Whether the stack is active
- `created_at`: Creation timestamp

#### Bet
- `id`: Unique identifier
- `stack_id`: Reference to the stack
- `payment_hash`: LNbits payment hash
- `amount`: Bet amount in sats
- `user_id`: User identifier (optional)
- `created_at`: When the bet was placed
- `is_winner`: Whether this bet won

#### WinHistory
- `id`: Unique identifier
- `stack_id`: Reference to the stack
- `bet_id`: Reference to the winning bet
- `amount_won`: Amount won in sats
- `user_id`: User identifier (optional)
- `timestamp`: When the win occurred

### API Endpoints

#### Public Endpoints
- `GET /api/v1/stacks` - List all available stacks
- `GET /api/v1/stacks/{stack_id}` - Get details of a specific stack
- `POST /api/v1/stacks/{stack_id}/bet` - Place a bet on a stack
- `GET /api/v1/bets/{bet_id}` - Check the status of a bet

#### Admin Endpoints
- `GET /api/v1/admin/stacks` - List all stacks (admin view)
- `POST /api/v1/admin/stacks` - Create a new stack
- `PUT /api/v1/admin/stacks/{stack_id}` - Update stack configuration
- `DELETE /api/v1/admin/stacks/{stack_id}` - Delete a stack
- `GET /api/v1/admin/stacks/{stack_id}/history` - View win history for a stack

## Development

### Project Structure

```
satsball/
├── __init__.py
├── manifest.json
├── migrations.py
├── views.py
├── views_api.py
├── models.py
├── crud.py
├── utils.py
├── webhook.py
├── templates/
│   └── satsball/
│       ├── index.html
│       ├── admin.html
│       ├── payment.html
│       ├── history.html
│       └── error.html
└── static/
    └── satsball/
        ├── style.css
        └── script.js
```

## Security Considerations

- All API endpoints validate permissions appropriately
- Payment webhooks are verified to prevent tampering
- Random number generation for probability calculations is cryptographically secure
- Proper input validation on all user-submitted data
- Protection against race conditions in stack amount updates

## License

This project is licensed under the MIT License.