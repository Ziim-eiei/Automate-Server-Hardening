import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import NoPage from "./pages/NoPage.jsx";
import AuditPage from "./pages/AuditPage.jsx";
import { NextUIProvider } from "@nextui-org/react";
import CreateProject from "./pages/CreateProject.jsx";
import ManageProject from "./pages/ManageProject.jsx";
import ManageServer from "./pages/ManageServer.jsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <CreateProject />,
  },
  {
    path: "/project",
    element: <ManageProject />,
  },
  {
    path: "/server",
    element: <ManageServer />,
  },
  {
    path: "/server/:projectId",
    element: <ManageServer />,
  },
  {
    path: "/hardening",
    element: <AuditPage />,
  },
  {
    path: "/hardening/:serverId",
    element: <AuditPage />,
  },
  {
    path: "*",
    element: <NoPage />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* <App /> */}
    <NextUIProvider>
      <RouterProvider router={router} />
    </NextUIProvider>
  </React.StrictMode>
);
