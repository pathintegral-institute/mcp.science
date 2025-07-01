# Timer MCP Server

This is a minimal [MCP](https://modelcontextprotocol.io) server that acts as a
count-down timer.  It exposes a single tool `wait` that:

* Takes two arguments, both in **milliseconds**:
  * `time_to_wait` – total duration to wait before the tool call completes.
  * `notif_interval` – interval between progress-update notifications.
* Sends progress updates every `notif_interval` milliseconds while waiting.
* Finishes once `time_to_wait` has elapsed and returns a text confirmation.

The server is primarily intended as a reference implementation that
demonstrates how to stream incremental updates from a long-running task back
to the client via MCP notifications.

## Running locally

```bash
# Using uvx (recommended – it will build an isolated virtual-env automatically)
uvx mcp-science timer

# Or, from the server directory via Python directly:
python -m timer
```

The tool can be invoked from any MCP-compatible client with a prompt similar
to:

>  "Please wait for 5 seconds, sending progress every 1 second."

```jsonc
{
  "tool": "wait",
  "time_to_wait": 5000,
  "notif_interval": 1000
}
```

You should receive five progress notifications followed by the final "done"
response.

