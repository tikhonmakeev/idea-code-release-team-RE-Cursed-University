import { useState } from 'react'
import Header from './components/Hedaer/Header'
import Search from './components/Search/Search'
import SearchWindow from './components/SearchWindow/SearchWindow'

function App() {
  return (
    <>
      <Header></Header>
      <main className="main">

        <SearchWindow></SearchWindow>
      </main>
    </>
  )
}

export default App
