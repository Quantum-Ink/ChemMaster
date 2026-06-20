// Wails Go bindings wrapper.
// In production: calls window.go.app.App.* (Wails v2 generated bindings)
// In dev mode: falls back to mock implementations.

import * as WailsApp from '../wailsjs/go/app/App'

// Wails v2 injects window.go.app.App at runtime
declare global {
  interface Window {
    go?: {
      app?: {
        App?: Record<string, (...args: any[]) => Promise<any>>
      }
    }
    runtime?: Record<string, (...args: any[]) => any>
  }
}

function hasGo(): boolean {
  return typeof window !== 'undefined' && !!window.go?.app?.App
}

// Direct wrapper — in Wails builds, uses generated bindings; in dev, returns null → falls back to mock
function call(method: string, ...args: any[]): Promise<any> {
  const mod = WailsApp as Record<string, (...a: any[]) => Promise<any>>
  const fn = mod[method]
  if (fn && hasGo()) return fn(...args)
  return Promise.resolve(null)
}

// === Formula API ===
export function parseFormula(formula: string) {
  return call('ParseFormula', formula).then(r => r ?? mockParseFormula(formula))
}
export function balanceEquation(equation: string) {
  return call('BalanceEquation', equation).then(r => r ?? mockBalanceEquation(equation))
}
export function processEquation(equation: string) {
  return call('ProcessEquation', equation).then(r => r ?? { original: equation, balanced: equation, isBalanced: false, subscript: equation, latex: `\\ce{${equation}}`, elements: {} })
}
export function analyzeIons(equation: string) {
  return call('AnalyzeIons', equation).then(r => r ?? { molecular: equation, fullIonic: equation, netIonic: equation, spectators: [], chargeBalanced: true })
}
export function balanceIonEquation(equation: string) {
  return call('BalanceIonEquation', equation).then(r => r ?? mockBalanceEquation(equation))
}
export function parseIon(ionStr: string) {
  return call('ParseIon', ionStr).then(r => r ?? { formula: ionStr, symbol: ionStr, charge: 0, isCation: false })
}
export function renderFormula(formula: string) {
  return call('RenderFormula', formula).then(r => r ?? { latex: `\\ce{${formula}}`, markdown: formula, html: formula, unicode: formula })
}
export function renderEquation(equation: string) {
  return call('RenderEquation', equation).then(r => r ?? { latex: `\\ce{${equation}}`, markdown: equation, html: equation, unicode: equation })
}

// === Database API ===
export function getElement(symbol: string) { return call('GetElement', symbol) }
export function searchElements(query: string) { return call('SearchElements', query).then(r => r ?? []) }
export function getAllElements() { return call('GetAllElements').then(r => r ?? []) }
export function searchCompounds(query: string) { return call('SearchCompounds', query).then(r => r ?? []) }

// === Provider API ===
export function listProviders() { return call('ListProviders').then(r => r ?? []) }
export function searchCompoundOnline(query: string) { return call('SearchCompoundOnline', query).then(r => r ?? []) }
export function setProviderEnabled(name: string, enabled: boolean) { return call('SetProviderEnabled', name, enabled) }
export function testProviderConnection(name: string) { return call('TestProviderConnection', name).then(r => r ?? '后端未连接') }

// === Plugin API ===
export function listPlugins() { return call('ListPlugins').then(r => r ?? []) }
export function setPluginEnabled(name: string, enabled: boolean) { return call('SetPluginEnabled', name, enabled) }

// === Settings API ===
export function getSetting(key: string) { return call('GetSetting', key).then(r => r ?? '') }
export function setSetting(key: string, value: string) { return call('SetSetting', key, value) }

// ============================================================
// Mock for dev mode (vite dev server without Wails runtime)
// ============================================================

function mockParseFormula(formula: string) {
  const masses: Record<string, number> = {
    H: 1.008, He: 4.003, Li: 6.941, Be: 9.012, B: 10.81, C: 12.011,
    N: 14.007, O: 15.999, F: 18.998, Ne: 20.18, Na: 22.99, Mg: 24.305,
    Al: 26.982, Si: 28.086, P: 30.974, S: 32.065, Cl: 35.453, Ar: 39.948,
    K: 39.098, Ca: 40.078, Fe: 55.845, Cu: 63.546, Zn: 65.38, Ag: 107.87,
    Au: 196.97, Hg: 200.59, Pb: 207.2, Mn: 55.938, Cr: 51.996, Ni: 58.693,
    Ba: 137.33, Sr: 87.62, Br: 79.904, I: 126.9,
  }
  const elements: Record<string, number> = {}
  let mw = 0
  const stack: [Record<string, number>, number][] = []
  let current: Record<string, number> = {}
  let i = 0
  while (i < formula.length) {
    const ch = formula[i]
    if (ch === '(' || ch === '[') { stack.push([current, 0]); current = {}; i++ }
    else if (ch === ')' || ch === ']') {
      i++; let num = ''
      while (i < formula.length && formula[i] >= '0' && formula[i] <= '9') { num += formula[i]; i++ }
      const mult = num ? parseInt(num) : 1
      const [prev] = stack.pop()!
      for (const [elem, cnt] of Object.entries(current)) prev[elem] = (prev[elem] || 0) + cnt * mult
      current = prev
    } else if (ch >= 'A' && ch <= 'Z') {
      let elem = ch; i++
      while (i < formula.length && formula[i] >= 'a' && formula[i] <= 'z') { elem += formula[i]; i++ }
      let num = ''
      while (i < formula.length && formula[i] >= '0' && formula[i] <= '9') { num += formula[i]; i++ }
      current[elem] = (current[elem] || 0) + (num ? parseInt(num) : 1)
    } else { i++ }
  }
  for (const [elem, count] of Object.entries(current)) { elements[elem] = count; mw += (masses[elem] || 0) * count }
  const sub = (s: string) => s.replace(/\d/g, d => '₀₁₂₃₄₅₆₇₈₉'[parseInt(d)])
  return { original: formula, elements, molecularWeight: Math.round(mw * 1000) / 1000, subscript: sub(formula), latex: `\\ce{${formula}}`, isValid: true }
}

function mockBalanceEquation(equation: string) {
  return { original: equation, balanced: equation, coefficients: [], isBalanced: false, elements: [], subscript: equation, latex: `\\ce{${equation}}`, error: '请使用 Wails 构建以使用配平功能' }
}
