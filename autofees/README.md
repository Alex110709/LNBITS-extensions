# Auto Channel Fees

Automatically adjust Lightning Network channel fees based on liquidity balance and network conditions.

## Overview

Auto Channel Fees helps Lightning node operators optimize their routing revenue by automatically adjusting channel fees based on liquidity distribution. The extension monitors your channels and adjusts fees to:

- **Discourage outbound payments** when local liquidity is low (increase fees)
- **Encourage outbound payments** when local liquidity is high (decrease fees)
- **Maintain optimal routing position** by balancing channel liquidity

## Features

### Fee Adjustment Strategies

1. **Balanced Strategy** (Recommended)
   - Moderate fee adjustments based on liquidity levels
   - Gradual changes to avoid drastic fee swings
   - Best for most node operators

2. **Aggressive Strategy**
   - Large fee adjustments for rapid rebalancing
   - Maximum fees when liquidity is low
   - Minimum fees when liquidity is high
   - Use with caution

3. **Conservative Strategy**
   - Small fee adjustments around default values
   - Minimal changes for stability
   - Safest option for risk-averse operators

### Key Features

- **Multiple Policies**: Create different policies for different channel groups
- **Liquidity Thresholds**: Define what "low" and "high" liquidity means
- **Fee Ranges**: Set minimum and maximum fee bounds
- **Gradual Adjustments**: Limit fee changes per adjustment cycle
- **Channel Filters**: Apply policies only to active channels or channels above a certain size
- **Adjustment History**: Track all fee changes with reasons
- **Manual Triggers**: Immediately apply adjustments without waiting for schedule
- **Statistics**: View adjustment performance and patterns

## How to Use

### 1. Create a Fee Policy

1. Click "New Policy" button
2. Configure your policy:
   - **Name**: Descriptive name for the policy
   - **Strategy**: Choose balanced, aggressive, or conservative
   - **Fee Range**: Set minimum and maximum fee rates (in ppm)
   - **Default Fee**: Fee rate for balanced liquidity
   - **Liquidity Thresholds**: Define low (<20%) and high (>80%) levels
   - **Auto-Adjustment**: Enable/disable automatic adjustments
   - **Adjustment Interval**: How often to check and adjust (in seconds)
   - **Channel Filters**: Minimum size, active only, etc.

3. Click "Save"

### 2. Monitor and Manage

- **View Policies**: See all your active policies and their settings
- **Enable/Disable**: Toggle policies on/off as needed
- **Trigger Manually**: Force immediate fee adjustment
- **View History**: See past adjustments with reasons and results
- **Check Statistics**: Analyze adjustment patterns and success rates

### 3. Understanding Fee Adjustments

The extension calculates optimal fees based on:

```
Liquidity Ratio = (Local Balance / Channel Capacity) × 100%
```

**Example with Balanced Strategy:**

- Liquidity < 20%: High fees (80-100% of max) - discourage outbound
- Liquidity 20-40%: Medium-high fees (60-80% of max)
- Liquidity 40-60%: Default fees - balanced state
- Liquidity 60-80%: Medium-low fees (40-60% of max)
- Liquidity > 80%: Low fees (20-40% of max) - encourage outbound

## Configuration Examples

### Basic Setup for New Node

```
Name: Default Policy
Strategy: Balanced
Fee Range: 10-2000 ppm
Default: 500 ppm
Low Threshold: 20%
High Threshold: 80%
Interval: 3600 seconds (1 hour)
```

### Aggressive Rebalancing

```
Name: Aggressive Rebalance
Strategy: Aggressive
Fee Range: 1-5000 ppm
Default: 500 ppm
Low Threshold: 25%
High Threshold: 75%
Interval: 1800 seconds (30 minutes)
```

### Conservative Management

```
Name: Conservative
Strategy: Conservative
Fee Range: 100-1000 ppm
Default: 500 ppm
Low Threshold: 15%
High Threshold: 85%
Interval: 7200 seconds (2 hours)
```

## API Endpoints

### Policy Management

- `POST /api/v1/policies` - Create new policy
- `GET /api/v1/policies` - List all policies
- `GET /api/v1/policies/{id}` - Get policy details
- `PUT /api/v1/policies/{id}` - Update policy
- `DELETE /api/v1/policies/{id}` - Delete policy

### Policy Actions

- `POST /api/v1/policies/{id}/trigger` - Manually trigger adjustment
- `POST /api/v1/policies/{id}/enable` - Enable policy
- `POST /api/v1/policies/{id}/disable` - Disable policy

### History & Statistics

- `GET /api/v1/policies/{id}/adjustments` - Get adjustment history
- `GET /api/v1/adjustments` - Get recent adjustments
- `GET /api/v1/policies/{id}/stats` - Get policy statistics

### Utility

- `GET /api/v1/strategies` - List available strategies
- `GET /api/v1/defaults` - Get default policy settings

## Background Processing

The extension requires periodic execution of the adjustment task. This should be set up as a cron job or scheduled task:

### Using Cron (Linux)

```bash
# Run every hour
0 * * * * python -c "import asyncio; from autofees.tasks import run_autofee_adjustment; asyncio.run(run_autofee_adjustment())"
```

### Using Python Scheduler

```python
import asyncio
import schedule
import time
from autofees.tasks import run_autofee_adjustment

def job():
    asyncio.run(run_autofee_adjustment())

schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Technical Details

### Fee Calculation Logic

The extension uses the following formula for fee calculation:

1. Calculate liquidity ratio: `ratio = local_balance / capacity`
2. Determine adjustment direction based on thresholds
3. Calculate target fee rate based on strategy
4. Apply gradual adjustment limit (max change per step)
5. Clamp to min/max bounds

### Database Schema

**Policies Table:**
- Policy configuration
- Strategy and thresholds
- Fee ranges and defaults
- Adjustment settings

**Adjustments Table:**
- Historical record of all fee changes
- Old and new fee values
- Reason for adjustment
- Success/failure status
- Liquidity ratio at time of adjustment

## Important Notes

### Lightning Node Integration

⚠️ **Important**: This extension requires integration with your Lightning node (LND or CLN) to:
- Fetch channel information
- Update channel fees

The current implementation includes placeholder functions in `tasks.py` that need to be replaced with actual Lightning node API calls:

- `get_channels_from_wallet()` - Fetch channel list and balances
- `update_channel_fees()` - Update fees via Lightning node

### Recommended Settings

- Start with **Balanced** strategy
- Use **1-hour intervals** initially
- Set **reasonable fee ranges** (10-2000 ppm is common)
- Monitor **adjustment history** regularly
- Adjust thresholds based on your routing patterns

### Best Practices

1. **Test First**: Start with one policy on a subset of channels
2. **Monitor Closely**: Watch adjustment history for first few cycles
3. **Adjust Gradually**: Fine-tune thresholds based on results
4. **Set Reasonable Bounds**: Avoid extreme min/max values
5. **Consider Network**: Higher fees during high demand periods

## Troubleshooting

### Policies Not Adjusting

- Check policy is **enabled**
- Verify **auto_adjust** is true
- Ensure background task is running
- Check adjustment interval hasn't passed

### Too Many Adjustments

- Increase **adjustment_interval**
- Raise **max_adjustment_per_step** limit
- Widen liquidity threshold ranges
- Switch to **conservative** strategy

### Fees Not Changing Enough

- Lower **max_adjustment_per_step** limit
- Narrow liquidity threshold ranges
- Switch to **aggressive** strategy
- Reduce adjustment interval

## Future Enhancements

Potential improvements for future versions:

- Integration with routing metrics (success rate, volume)
- Machine learning for optimal fee prediction
- Channel-specific policies based on peer characteristics
- Integration with rebalancing tools
- Network-wide fee analysis and recommendations
- Multi-node policy synchronization
- Advanced reporting and analytics

## Contributing

Contributions are welcome! Areas for improvement:

- Lightning node integration (LND/CLN)
- Additional adjustment strategies
- Enhanced statistics and reporting
- Fee optimization algorithms
- Performance improvements

## References

- [Lightning Network Fee Management](https://docs.lightning.engineering/the-lightning-network/routing-fees)
- [LND Fee Management](https://docs.lightning.engineering/lightning-network-tools/lnd/channel-fees)
- [CLN Plugin Development](https://docs.corelightning.org/docs/plugin-development)

## License

MIT License - See LNBits main repository for details
