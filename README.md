# Automate Server Hardening

## Introduction

This web application allows you to harden your servers based on the CIS Benchmark. The CIS Benchmark is a set of security recommendations for a variety of operating systems and applications. Hardening your servers will help to protect them from a variety of threats.

## Features

- Select the hardening topics you want to apply
- Audit your server configuration
- Perform automated hardening

## Limitaions

- Only work with Windows Server 2019
- Complete hardening and auditing of account policies and local policies only
- Recommend running on localhost only

## Quick Start

Pull latest image:

```
docker pull ghcr.io/ziim-eiei/automate-server-hardening:latest
```

Run container:

```
docker run --name ash -d -p 80:80 -p 8000:8000 ghcr.io/ziim-eiei/automate-server-hardening:latest
```

Access web app:

open on browser: <a href="http://localhost" target="_blank">http://localhost</a>
