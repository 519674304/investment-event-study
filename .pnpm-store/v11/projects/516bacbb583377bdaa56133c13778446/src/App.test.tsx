import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App";

afterEach(() => vi.restoreAllMocks());

test("selects a research object and shows its events below the chart", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    if (url === "/api/research-objects") {
      return Response.json([
        { id: "hog", market: "CN", code: "884275", name: "生猪养殖", type: "concept_index" }
      ]);
    }
    if (url === "/api/events?researchObjectId=hog") {
      return Response.json([
        {
          id: "event-1",
          publishedOn: "2026-08-09",
          title: "居民猪肉价格环比上涨",
          summary: "事件完整摘要放在图表下方。",
          sourceName: "国家统计局",
          sourceUrl: "https://example.com/source",
          categoryId: "product-price",
          tags: ["猪价"],
          linkedResearchObjectIds: ["hog"]
        }
      ]);
    }
    throw new Error(`Unexpected request: ${url}`);
  });

  render(<App />);
  await userEvent.click(await screen.findByRole("button", { name: /生猪养殖/ }));

  expect(await screen.findByRole("heading", { name: "生猪养殖" })).toBeInTheDocument();
  expect(screen.getByLabelText("K 线图区域")).toBeInTheDocument();
  expect(screen.getByText("居民猪肉价格环比上涨")).toBeInTheDocument();
  expect(screen.getByText("事件完整摘要放在图表下方。")).toBeInTheDocument();
  await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/events?researchObjectId=hog"));
});
