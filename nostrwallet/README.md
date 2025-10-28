# Nostr Wallet Connect (NIP-47)

LNBits extension for connecting your Lightning wallet to Nostr applications using the NIP-47 protocol.

## What is NIP-47?

NIP-47 (Nostr Wallet Connect) is a protocol that allows Nostr applications to interact with Lightning wallets. It uses Nostr's decentralized relay network to securely communicate wallet commands between applications and wallets.

## Features

- Create multiple wallet connections with different permissions
- Generate connection strings (nostr+walletconnect:// URIs)
- QR code generation for easy mobile setup
- Granular permission control per connection
- Support for standard NIP-47 methods:
  - `pay_invoice` - Pay Lightning invoices
  - `make_invoice` - Create new invoices
  - `get_balance` - Check wallet balance
  - `get_info` - Get wallet information
  - `lookup_invoice` - Check invoice status
  - `list_transactions` - View transaction history

## How to Use

1. **Create a Connection**
   - Click "New Connection" button
   - Give your connection a name (e.g., "My Nostr App")
   - Select a Nostr relay (default: wss://relay.damus.io)
   - Choose which permissions to grant
   - Click "Create"

2. **Connect to Nostr App**
   - Click the QR code icon next to your connection
   - Scan the QR code with your Nostr app, or
   - Copy the connection string and paste it into your app

3. **Manage Connections**
   - View all active connections
   - Toggle connections on/off
   - Delete connections you no longer need
   - Monitor last usage time

## Security Notes

- Each connection has its own keypair and permissions
- You can revoke access at any time by deleting the connection
- Connection secrets are stored securely in your LNBits database
- Only grant necessary permissions to each connection
- Regularly review and clean up unused connections

## Supported Nostr Wallets & Apps

This extension is compatible with any Nostr application that implements NIP-47, including:

- Amethyst (Android Nostr client)
- Damus (iOS Nostr client)
- Alby Browser Extension
- Nostr zap-enabled applications

## Technical Details

### Connection String Format

```
nostr+walletconnect://<pubkey>?relay=<relay-url>&secret=<secret>
```

### Permissions

Each connection can be granted specific permissions:

- `pay_invoice` - Allow paying Lightning invoices
- `make_invoice` - Allow creating new invoices
- `get_balance` - Allow checking wallet balance
- `get_info` - Allow getting wallet info
- `lookup_invoice` - Allow looking up invoice status
- `list_transactions` - Allow viewing transaction list

### API Endpoints

- `POST /api/v1/connections` - Create new connection
- `GET /api/v1/connections` - List all connections
- `GET /api/v1/connections/{id}` - Get specific connection
- `PUT /api/v1/connections/{id}` - Update connection
- `DELETE /api/v1/connections/{id}` - Delete connection
- `GET /api/v1/info/{id}` - Get connection string
- `POST /api/v1/nip47/request` - Process NIP-47 requests

## Development Status

This is a basic implementation of NIP-47. Current limitations:

- Simplified Nostr keypair generation (use proper secp256k1 in production)
- Basic encryption implementation (enhance for production use)
- Relay communication not fully implemented
- Additional NIP-47 methods can be added

## Contributing

Contributions are welcome! Areas for improvement:

- Full secp256k1 keypair generation
- NIP-04 encryption/decryption implementation
- WebSocket relay connection handling
- Additional NIP-47 method implementations
- Enhanced error handling
- Rate limiting and abuse prevention

## References

- [NIP-47 Specification](https://github.com/nostr-protocol/nips/blob/master/47.md)
- [Nostr Protocol](https://nostr.com)
- [LNBits Documentation](https://docs.lnbits.org)

## License

MIT License - See LNBits main repository for details
