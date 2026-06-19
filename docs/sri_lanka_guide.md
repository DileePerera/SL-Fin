# 🇱🇰 Sri Lanka Guide - Local Finance Agent

This guide is specifically written for users in **Sri Lanka** to help you get the best results from **Local Finance Agent**.

---

## Supported Sri Lankan Banks

The system currently works well with the following banks:

| Bank                      | CSV Support | PDF Support | Notes |
|--------------------------|-------------|-------------|-------|
| Commercial Bank          | Excellent   | Good        | Most common format |
| Bank of Ceylon (BOC)     | Good        | Fair        | Sometimes needs LLM fallback |
| Sampath Bank             | Excellent   | Good        | Clean data |
| Nations Trust Bank       | Good        | Good        | - |
| HSBC                     | Excellent   | Excellent   | Very structured |
| Hatton National Bank     | Good        | Fair        | - |
| People's Bank            | Good        | Fair        | - |
| DFCC / NDB               | Good        | Good        | - |

**Tip**: CSV exports usually give the best accuracy.

---

## Common Sri Lankan Expense Categories

The AI is trained to recognize these categories:

- **Food & Dining** (Hotel, Bake House, Perera & Sons, KFC, McDonalds, etc.)
- **Transport** (Petrol, Uber, PickMe, Bus, Train)
- **Utilities** (CEB, NWSDB, Dialog, Mobitel, SLT)
- **Rent / Home**
- **Shopping** (Keells, Arpico, Fashion, Cargills)
- **Healthcare** (Hospitals, Pharmacies, Asiri, Nawaloka)
- **Education** (School fees, Tuition, University)
- **Bills & EMI**
- **Savings & Investments** (Unit Trusts, Fixed Deposits, CSE)
- **Others**

---

## Installation Tips for Sri Lanka

### Hardware Recommendations

- **Minimum**: 16GB RAM + 6GB VRAM (RTX 3060 / RTX 4060)
- **Recommended**: 32GB RAM + 8GB+ VRAM
- **Best**: 64GB RAM (for running 32B+ models comfortably)

**Power Tip**: Use quantized models (`q4_K_M` or `q5_K_M`) to save VRAM.

### Installing Ollama on Windows

1. Download Ollama from [ollama.com](https://ollama.com)
2. Run these commands in PowerShell:

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:32b
ollama pull phi-4