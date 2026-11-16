import test from "node:test";
import assert from "node:assert/strict";
import {parseCsvText} from "../lib/csv.js";
test("Detects Google tab separated export with metadata",()=>{
 const text="Report\nLast 30 days\nCampaign\tCost\tImpressions\tClicks\tConversions\nBrand\t300\t1000\t100\t7";
 const data=parseCsvText(text);
 assert.equal(data.skippedLines,2);
 assert.equal(data.rows[0].Campaign,"Brand");
 assert.equal(data.mapping.spend,"Cost");
});
test("Parses Meta comma separated CSV header",()=>{
 const data=parseCsvText("Campaign Name,Amount Spent (USD),Impressions,Link Clicks,Results\nProspecting,100,5000,50,4");
 assert.equal(data.rows.length,1);
 assert.equal(data.mapping.conversions,"Results");
});
