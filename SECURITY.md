# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.4.x | :white_check_mark: |
| 0.3.x | :white_check_mark: (critical fixes only) |
| < 0.3 | :x: |

## Scope

`ai-character-sheet-turnaround` is a local desktop tool. The main security
surfaces are:

1. **Remote renderer backends.** If you configure a remote endpoint (e.g. a
   self-hosted ComfyUI or an Autograd node), the app will POST your prompt and
   optional reference image to it. Only point it at servers you control or
   trust. The URL is validated against an allowlist in
   `services/remote_renderer.py`.
2. **Model weight loading.** We only load `.safetensors` and `.ckpt` files
   from `weights/`. `torch.load` is called with `weights_only=True`. Do not
   add arbitrary pickle loading.
3. **Plugin handlers.** `handlers/` is loaded dynamically at startup. A
   malicious handler is arbitrary code execution. Only run this repo from a
   trusted checkout.

## Reporting a vulnerability

Email `security@<your-domain>` (or open a private security advisory on GitHub)
with:

- A description of the issue.
- A minimal repro (prompt, config, and if relevant, a malicious plugin).
- The affected version.

We aim to acknowledge within 72 hours. Please do not open public issues for
exploits until a fix has shipped.

## Out of scope

- The content of generated images. This tool renders fictional characters.
  What you do with the outputs is your problem, not ours.
- Bug reports from forks.
- Anything requiring physical access to an unlocked machine.