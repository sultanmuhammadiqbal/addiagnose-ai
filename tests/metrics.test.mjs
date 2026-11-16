import test from "node:test";
import assert from "node:assert/strict";
import { guessMapping, numeric, standardizeRows } from "../lib/metrics.js";
import { analyzeCopy } from "../lib/copy.js";

test("Parses localized currency", () => {
  assert.equal(numeric("Rp 1.234.567,89"),1234567.89);
  assert.equal(numeric("$1,234.50"),1234.5);
  assert.equal(numeric("1 234,50"),1234.5);
});
test("Maps Meta Ads without phantom ratios",()=>{
  const headers = ["Campaign Name","Amount Spent (USD)","Impressions","Link Clicks","Results"];
  const mapping=guessMapping(headers);
  assert.equal(mapping.spend,"Amount Spent (USD)");
  assert.equal(mapping.clicks,"Link Clicks");
  const result=standardizeRows([{
    "Campaign Name":"One","Amount Spent (USD)":"200","Impressions":"2000","Link Clicks":"100","Results":"5"
  }],mapping);
  assert.equal(result.rows[0].ctr,5);
  assert.equal(result.rows[0].cvr,5);
  assert.equal(result.rows[0].cpc,2);
  assert.equal(result.rows[0].cpa,40);
});
test("Rejects invalid counts instead of replacing with zero",()=>{
  const mapping={campaign:"Campaign",spend:"Spend",impressions:"Impressions",clicks:"Clicks",conversions:"Conversions"};
  assert.throws(()=>standardizeRows([{Campaign:"A",Spend:"4",Impressions:"??",Clicks:"2",Conversions:"1"}],mapping));
});
test("Counts emoji correctly",()=>{
  const result=analyzeCopy("Apakah kamu siap? Beli sekarang! 🔥🚀");
  assert.equal(result.emojis,2);
  assert.equal(result.hook,true);
  assert.equal(result.foundCta.includes("beli"),true);
});
