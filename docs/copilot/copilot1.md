Great! To list all services and environments under the `tts-next-fast-aws` application, you can run:

```bash
# List all environments in the application
copilot env ls --app tts-next-fast-aws
```

This will show something like:

```
Name    AccountID        Region
dev     681916125840     us-east-1
prod    681916125840     us-east-1
```

Then, to list all services in the application:

```bash
copilot svc ls --app tts-next-fast-aws
```

You’ll see output like:

```
Name      Type       Environments
backend   Backend    dev, prod
frontend  Load Balanced Web Service   dev, prod
```

Finally, to see the **URLs for a specific service**:

```bash
copilot svc show --name backend --env dev
```

This will give details including the **service endpoint** (public URL), task status, and health.

If you want, I can write a **single command sequence to show everything at once** for quick reference. Do you want me to do that?
