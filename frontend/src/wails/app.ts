// Wails Go bindings wrapper.
// Uses auto-generated bindings from wailsjs/go/app/App.js

import * as App from '../wailsjs/go/app/App'

// Formula
export const parseFormula = App.ParseFormula
export const balanceEquation = App.BalanceEquation
export const processEquation = App.ProcessEquation
export const analyzeIons = App.AnalyzeIons
export const balanceIonEquation = App.BalanceIonEquation
export const parseIon = App.ParseIon
export const renderFormula = App.RenderFormula
export const renderEquation = App.RenderEquation

// Database
export const getElement = App.GetElement
export const searchElements = App.SearchElements
export const getAllElements = App.GetAllElements
export const searchCompounds = App.SearchCompounds

// Providers
export const listProviders = App.ListProviders
export const searchCompoundOnline = App.SearchCompoundOnline
export const setProviderEnabled = App.SetProviderEnabled
export const testProviderConnection = App.TestProviderConnection

// Plugins
export const listPlugins = App.ListPlugins
export const setPluginEnabled = App.SetPluginEnabled

// Settings
export const getSetting = App.GetSetting
export const setSetting = App.SetSetting
