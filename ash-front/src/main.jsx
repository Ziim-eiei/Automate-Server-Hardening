import React from 'react'
import ReactDOM from 'react-dom/client'
// import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Test from './pages/Test.jsx'
import Home from './pages/Home.jsx'
import NoPage from './pages/NoPage.jsx'
import AuditPage from './pages/AuditPage.jsx';

import {NextUIProvider} from '@nextui-org/react'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Test/>,
  },
  {
    path: "/home",
    element: <Home/>,
  },
  {
    path: "/audit",
    element: <AuditPage/>,
  },
  {
    path: "*",
    element: <NoPage/>,
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* <App /> */}
    <NextUIProvider>
    <RouterProvider router={router} />
    </NextUIProvider>
  </React.StrictMode>,
)
