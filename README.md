# 💳 3-D Secure Payment Flow Simulator

> 3DS Authentication Flow (Initiate → OTP → Verify → CAVV)  
> Built by [Tajudeen Jalaudin](https://github.com/Tajudeenj)

## Overview

Simulates the complete **3-D Secure (3DS)** authentication flow for card-based digital transactions — enrollment check, OTP dispatch, verification, and CAVV generation. Based on live 3DS implementation for UAE, UK & Iraq at ADIB.

## 3DS Flow

```
POST /api/v1/3ds/initiate  → Check enrollment, send OTP
POST /api/v1/3ds/verify    → Verify OTP → CAVV + ECI
GET  /api/v1/3ds/session/{id} → Session status
```

## ECI Codes

| ECI | Meaning |
|-----|---------|
| 05 | Full 3DS authentication — issuer liable |
| 07 | Not enrolled / failed — merchant liable |

## Test Cards

| Card | Status | OTP |
|------|--------|-----|
| 4111111111111111 | Enrolled (UAE) | 123456 |
| 4222222222222222 | Enrolled (UK) | 654321 |
| 4000000000000000 | Not enrolled | N/A |

## Quick Start

```bash
git clone https://github.com/Tajudeenj/3ds-payment-flow-simulator.git
cd 3ds-payment-flow-simulator
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

## Related Skills

`3-D Secure` `Payment Security` `Card Authentication` `CAVV` `ECI` `FastAPI` `UAE Banking`

---
*Part of the [Tajudeen Jalaudin](https://github.com/Tajudeenj) Banking Tech Portfolio*
