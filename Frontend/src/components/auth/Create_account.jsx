import MobileValidator from "./MobileValidator";
import PasswordValidator from "./PasswordValidator";
import EmailValidator from "./EmailValidator";
import { useState } from "react";
export default function Create_account(){

    const [isValid, setIsValid]=useState(false);
    if(isValid){
        console.log('create')
    }

}