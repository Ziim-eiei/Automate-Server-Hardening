import React from 'react'
import '../css/cards.css'
import { MyInput } from "./Input"
import { SearchIcon } from "../components/SearchIcon"
import { Button, ButtonGroup } from "@nextui-org/react";
import { MyButton } from './MyButton';

function HardenTopper() {
    return (
        <div className='topper'>
            <h1 className='heading'>Select topic to Hardening & Audit</h1>
            <p className='projName'>Project name</p>
            <div className='row'>
                <p className='col topper-name'>Name</p>
                <MyInput isClearable startContent={<SearchIcon />} placeholder="Search yout topic" radius="full" color="warning" />
                <MyButton className='audit-btn'>Search</MyButton>
                <MyButton className='audit-btn'>Hardening</MyButton>
                <MyButton className='audit-btn'>Audit</MyButton>

            </div>
        </div>
    )
}

export default HardenTopper