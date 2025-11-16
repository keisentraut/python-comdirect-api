#!/usr/bin/env python3

# During development, you can store your credentials in bin/creds.py.
# Just put something like the following there:
#     user = "XXXXXXXX"
#     password = "XXXXXX"
#     client_id = "User_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#     client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Alternatively, just hard-code them here.

from creds import user, password, client_id, client_secret
from comdirect_api.session import Session

import json
import sys

out_path = sys.argv[1] if len(sys.argv) == 2 else None

s = Session(user, password, client_id, client_secret)

depots = s.account_get_depots()
if not depots:
    print("No depots found.")
    sys.exit(0)

output = {"depots": []}

for idx, depot in enumerate(depots, start=1):
    print(f"\n[{idx}] Depot {depot.depotDisplayId or depot.depotId}")

    # Use session method to get aggregated values
    balance, positions = None, None
    try:
        balance, positions = s.account_get_depot_positions(depot.depotId)
        if balance: 
            print("Summary:")
            print(f"\t Previous Day Value: {balance.prevDayValue} EUR")
            print(f"\t Current Value     : {balance.currentValue} EUR")
            print(f"\t Purchase Value    : {balance.purchaseValue} EUR")
            print(f"\t Profit Since Buy  : {balance.profitSincePurchase} EUR")
            print(f"\t 1-day Performance : {balance.profitLossPrevDayRel} %")
            print(f"\t Total Performance : {balance.profitLossPurchaseRel} %")

    except Exception as e:
        print(f"Failed to fetch depot data: {e}")

    if positions:
        print(f"Positions ({len(positions)}):")
        for i, pos in enumerate(positions, start=1):
            
            print(f"\t {i:>2}. WKN {pos.wkn}")
            print(f"\t\t Qty: {pos.qty} | Current: {pos.currentValue} EUR | Purchase: {pos.purchaseValue} EUR")
            print(f"\t\t Total P/L: {pos.profitLossPurchaseAbs} EUR | Total P/L {pos.profitLossPurchaseRel} % | 1-day P/L: {pos.profitLossPrevDayRel} %")
    else:
        print("\t No positions found.")

    # Collect JSON output for this depot
    output["depots"].append({
        "depotId": depot.depotId,
        "depotDisplayId": depot.depotDisplayId,
        "holderName": depot.holderName,
        "aggregated": None if not balance else {
            "prevDayValue": balance.prevDayValue,
            "currentValue": balance.currentValue,
            "purchaseValue": balance.purchaseValue,
            "profitSincePurchase": balance.profitSincePurchase,
            "profitLossPrevDayRel": balance.profitLossPrevDayRel,
            "profitLossPurchaseRel": balance.profitLossPurchaseRel,
        },
        "positions": [] if not positions else [
            {
                "wkn": p.wkn,
                "quantity": p.qty,
                "currentValue": p.currentValue,
                "purchaseValue": p.purchaseValue,
                "profitLossPurchaseAbs": p.profitLossPurchaseAbs,
                "profitLossPurchaseRel": p.profitLossPurchaseRel,
                "profitLossPrevDayAbs": p.profitLossPrevDayAbs,
                "profitLossPrevDayRel": p.profitLossPrevDayRel,
            }
            for p in positions
        ],
    })

# Save JSON if an output path was provided
if out_path:
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON to {out_path}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")