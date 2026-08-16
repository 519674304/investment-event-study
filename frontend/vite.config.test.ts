import config from "./vite.config";
import { expect, test } from "vitest";

test("forwards API requests to the local backend during development", () => {
  expect(config.server?.proxy?.["/api"]).toMatchObject({
    target: "http://127.0.0.1:8000"
  });
});
