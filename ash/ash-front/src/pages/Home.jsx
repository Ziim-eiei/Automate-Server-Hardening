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
            <Image width={100} alt="SIT Logo Image" src="/KMUTTSIT.png" />
          </NavbarBrand>

          <NavbarContent className="sm:flex gap-6 " justify="center">
            <NavbarItem>
              <Link href="#" className="text-lightblue">
                Home
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="/project" className="text-foreground2">
                Project
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="/hardening" className="text-foreground2">
                Detail
              </Link>
            </NavbarItem>

            <NavbarItem>
              <Link href="#" className="text-foreground2">
                Contact Us
              </Link>
            </NavbarItem>
          </NavbarContent>

          <NavbarContent justify="end">
            <NavbarItem>
              <Button
                onClick={() => {
                  window.open(
                    "https://github.com/Ziim-eiei/Automate-Server-Hardening"
                  );
                }}
                as={Link}
                href="#"
                variant="flat"
                className="text-foreground2 bg-transparent border-1 border-foreground2 rounded-md shadow-2xl"
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
              src="/iconServer.png"
            />
            <div class="dot"></div>
          </div>
        </div>
      </div>
    </>
  );
}
