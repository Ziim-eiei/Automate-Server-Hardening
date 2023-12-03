import React from 'react'
import { Input } from "@nextui-org/react";

// import { MyInput } from "./Input"
import { SearchIcon } from "../components/SearchIcon"
import { Button, ButtonGroup } from "@nextui-org/react";
import { TopperButton } from './TopperButton';

function HardenTopper() {
    return (
        <span className='topper'>
            <h1 className='heading'>Select topic to Hardening & Audit</h1>
            <p className='projName'>Project name</p>
            <div className='row'>
                <p className='col topper-name'>Name</p>
                <input className='topper-search' placeholder="Type to search..." />


                {/* <MyInput isClearable startContent={<SearchIcon />} placeholder="Search yout topic" radius="full" color="warning" /> */}
                {/* <TopperButton className='topper-btn'>Search</TopperButton>
                <TopperButton className='topper-btn'>Hardening</TopperButton>
                <TopperButton className='topper-btn'>Audit</TopperButton> */}
            </div>
        </span>
    )
}

export default HardenTopper