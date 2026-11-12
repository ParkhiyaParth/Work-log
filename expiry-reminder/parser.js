// Turns the text inside a product QR code into {name, expiry:'YYYY-MM-DD'|null, batch, code}.
// Understands JSON, URLs with query params, GS1 (17)YYMMDD codes, "key: value" text, or any text containing a date.
(function (root) {
  const pad = n => String(n).padStart(2, '0');
  const iso = (y, m, d) => {
    const dt = new Date(Date.UTC(y, m - 1, d));
    return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d ? `${y}-${pad(m)}-${pad(d)}` : null;
  };
  const eom = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate();

  // UK style: day before month.
  function parseDate(s) {
    if (!s) return null;
    s = String(s).trim();
    let m;
    if ((m = s.match(/^(\d{4})[-\/.](\d{1,2})[-\/.](\d{1,2})$/))) return iso(+m[1], +m[2], +m[3]);
    if ((m = s.match(/^(\d{1,2})[-\/.](\d{1,2})[-\/.](\d{4})$/))) return iso(+m[3], +m[2], +m[1]);
    if ((m = s.match(/^(\d{1,2})[-\/.](\d{1,2})[-\/.](\d{2})$/))) return iso(2000 + +m[3], +m[2], +m[1]);
    if ((m = s.match(/^(\d{4})(\d{2})(\d{2})$/))) return iso(+m[1], +m[2], +m[3]);
    if ((m = s.match(/^(\d{1,2})[ -]([A-Za-z]{3,9})[ -,]*(\d{4})$/))) {
      const mo = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'].indexOf(m[2].slice(0, 3).toLowerCase());
      if (mo >= 0) return iso(+m[3], mo + 1, +m[1]);
    }
    if ((m = s.match(/^(\d{1,2})[-\/.](\d{4})$/))) return iso(+m[2], +m[1], eom(+m[2], +m[1])); // MM/YYYY -> end of month
    return null;
  }

  function gs1Date(yymmdd) {
    const y = 2000 + +yymmdd.slice(0, 2), mo = +yymmdd.slice(2, 4);
    let d = +yymmdd.slice(4, 6);
    if (d === 0) d = eom(y, mo);
    return iso(y, mo, d);
  }

  const KEYS = {
    name: ['name', 'product', 'title', 'item', 'description', 'desc'],
    expiry: ['expiry', 'expiry_date', 'expirydate', 'exp', 'expires', 'expiration', 'expiration_date', 'best_before', 'bestbefore', 'bb', 'bbe', 'use_by', 'useby'],
    batch: ['batch', 'lot', 'batch_no', 'batchno'],
    code: ['code', 'sku', 'barcode', 'gtin', 'id']
  };
  const pick = (obj, field) => {
    for (const k of Object.keys(obj)) if (KEYS[field].includes(k.toLowerCase().replace(/[\s-]/g, '_'))) return String(obj[k]);
    return '';
  };
  const fromObj = (o, text) => ({
    name: pick(o, 'name'), expiry: parseDate(pick(o, 'expiry')), batch: pick(o, 'batch'), code: pick(o, 'code'), raw: text
  });

  function parse(text) {
    text = String(text || '').trim();
    const out = { name: '', expiry: null, batch: '', code: '', raw: text };
    if (!text) return out;

    try { const j = JSON.parse(text); if (j && typeof j === 'object' && !Array.isArray(j)) return Object.assign(out, fromObj(j, text)); } catch (e) {}

    if (/^https?:\/\//i.test(text)) {
      try {
        const u = new URL(text), o = {};
        u.searchParams.forEach((v, k) => { o[k] = v; });
        const r = fromObj(o, text);
        if (r.name || r.expiry) { if (!r.code) r.code = text; return Object.assign(out, r); }
      } catch (e) {}
    }

    // GS1, with or without parentheses
    let m = text.match(/\(17\)(\d{6})/) || text.match(/^01\d{14}17(\d{6})/);
    if (m) {
      out.expiry = gs1Date(m[1]);
      const g = text.match(/\(01\)(\d{14})/) || text.match(/^01(\d{14})/);
      if (g) out.code = g[1];
      const b = text.match(/\(10\)([^(]+)/) || text.match(/^01\d{14}17\d{6}10(.+)$/);
      if (b) out.batch = b[1].trim();
      return out;
    }

    // "key: value" lines (separated by newline, ; | or &)
    const pairs = {};
    text.split(/[\n;|&]+/).forEach(p => { const kv = p.match(/^\s*([A-Za-z_ -]+?)\s*[:=]\s*(.+?)\s*$/); if (kv) pairs[kv[1]] = kv[2]; });
    if (Object.keys(pairs).length) {
      const r = fromObj(pairs, text);
      if (r.name || r.expiry || r.code) return Object.assign(out, r);
    }

    // last resort: look for a date anywhere; the rest is the name/code
    const dm = text.match(/\b(\d{4}[-\/.]\d{1,2}[-\/.]\d{1,2}|\d{1,2}[-\/.]\d{1,2}[-\/.]\d{2,4}|\d{1,2} [A-Za-z]{3,9},? \d{4})\b/);
    if (dm) { out.expiry = parseDate(dm[1]); text = text.replace(dm[1], '').replace(/[\s,;|:-]+$/, '').trim(); }
    if (/^\d{8,14}$/.test(text)) out.code = text; else out.name = text;
    return out;
  }

  const api = { parse, parseDate };
  if (typeof module !== 'undefined') module.exports = api; else root.QRParser = api;
})(this);
