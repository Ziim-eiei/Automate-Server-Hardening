import React from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Link,
  Button,
} from "@nextui-org/react";
import { useNavigate } from "react-router-dom";
import { MyButton } from "../components/Button";
import "../css/Homepage.css";
import { Image } from "@nextui-org/react";
import { Padding } from "@mui/icons-material";

export default function Home() {
  const navigate = useNavigate();
  return (
    <>
      <div className="homePage">
        <Navbar className="navBarHome" style={{ padding: "0px" }}>
          <NavbarBrand>
<<<<<<< HEAD
            <Image
              width={100}
              alt="SIT Logo Image"
              src="../../public/KMUTTSIT.png"
            />
=======
            <Image width={100} alt="SIT Logo Image" src="/KMUTTSIT.png" />
>>>>>>> dev
          </NavbarBrand>

          <NavbarContent className="sm:flex gap-6 " justify="center">
            <NavbarItem>
              <Link href="#" className="text-lightblue">
                Home
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="/project" color="foreground">
                Project
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="/hardening" color="foreground">
                Detail
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="#" color="foreground">
                Contact Us
              </Link>
            </NavbarItem>
          </NavbarContent>

          <NavbarContent justify="end">
            <NavbarItem>
              <Button
                onClick={() => {
                  window.open(
                    "https://www.cisecurity.org/benchmark/microsoft_windows_server"
                  );
                }}
                as={Link}
                href="#"
                variant="flat"
                className="text-foreground bg-transparent border-1 border-foreground rounded-md shadow-2xl"
              >
                Learn More
              </Button>
            </NavbarItem>
          </NavbarContent>
        </Navbar>

        <div className="homeContent">
          <h1 className="homePagetext">
            Automate Server <br /> Hardening
          </h1>
          <div style={{ textAlign: "left" }}>
            <MyButton
              onClick={() => {
                navigate("/project");
              }}
              className="homePageBtn"
            >
              Get Started
            </MyButton>
          </div>
          <div>
            <Image
              className="imgServer"
              alt="Server Image"
<<<<<<< HEAD
              src="../../public/iconServer.png"
=======
              src="/iconServer.png"
>>>>>>> dev
            />
            <div class="dot"></div>
          </div>
        </div>
      </div>
    </>
  );
}
