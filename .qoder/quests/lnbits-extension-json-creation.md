# LNbits Extension Registration JSON Creation

## Overview
This document describes the process of creating a JSON file for registering the SatsBall extension with LNbits. The SatsBall extension is a Bitcoin Lightning gambling extension that allows users to place bets using Bitcoin Lightning payments with multiple betting stacks.

## Extension Information
Based on the manifest.json file and code analysis, here is the information needed for the LNbits extension registration:

### Extension Registration JSON
```json
{
  "name": "SatsBall",
  "short_description": "Bitcoin Lightning gambling extension with multiple betting stacks",
  "version": "0.1.0",
  "author": "Your Name",
  "author_url": "https://github.com/yourusername",
  "icon": "dice",
  "description": "A gambling extension for LNbits that allows users to place bets using Bitcoin Lightning payments. Features multiple betting stacks where users can place bets at 1000 sats per bet. Each stack accumulates Bitcoin, and there's a probability-based mechanism for users to win all the Bitcoin in a stack.",
  "min_lnbits_version": "0.12.0",
  "dependencies": ["satspay"],
  "environments": ["core"]
}
```

## Data Models
The extension uses the following data models:

### Stack Model
- id (str): Unique identifier for the stack
- name (str): Name of the stack
- description (str): Description of the stack
- current_amount (int): Current accumulated amount in the stack
- bet_price (int): Price for placing a bet (fixed at 1000 sats)
- winning_probability (float): Probability of winning the stack
- fee_percentage (float): Fee percentage taken from bets
- enabled (bool): Whether the stack is enabled
- created_at (datetime): Timestamp when the stack was created

### Bet Model
- id (str): Unique identifier for the bet
- stack_id (str): Reference to the stack
- payment_hash (str): Lightning payment hash
- amount (int): Amount of the bet (1000 sats per bet)
- user_id (Optional[str]): User identifier
- created_at (datetime): Timestamp when the bet was created
- is_winner (bool): Whether this bet won

### Win History Model
- id (str): Unique identifier for the win record
- stack_id (str): Reference to the stack
- bet_id (str): Reference to the winning bet
- amount_won (int): Amount won
- user_id (Optional[str]): User identifier
- timestamp (datetime): Timestamp when the win occurred

## Database Tables
The extension uses three database tables:

1. stacks: Stores information about betting stacks
2. bets: Stores information about placed bets
3. win_history: Stores information about winning bets

## API Endpoints
The extension provides the following views:
- GET /: Main index page showing available stacks
- GET /admin: Admin page for managing stacks
- GET /payment/{stack_id}: Payment page for a specific stack

## Dependencies
The extension requires the following dependencies:
- satspay: For handling Lightning payments