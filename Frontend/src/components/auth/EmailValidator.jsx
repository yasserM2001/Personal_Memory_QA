import { memo } from "react";

function EmailValidator({email}){
    console.log('EmailValidator component rendered')

    const patt = /^[a-z0-9_.-]+@[a-z_.-]+\.[a-z]{2,}$/
    const isvalid =patt.test(email)

    const Len =() => <span className="text-sky-500">name@company.com</span>
    const Valid = () => <span className="text-green-500">Valid email</span> 
    const Invalid = () => <span className="text-red-500">please enter the correct form of email</span> 
    return(
        <div>
            <p className="text-xs">
                {(email.length == 0)? <Len/> : isvalid ? <Valid/> : <Invalid/>}            </p>
        </div>
    )
}
export default memo(EmailValidator);