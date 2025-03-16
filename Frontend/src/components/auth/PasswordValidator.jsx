import { memo } from "react";

function PasswordValidator({ password, passwordConfirmation }) {

    console.log('PasswordValidator Component Rendered');

    // Correct and Wrong Components
    const Correct = () => <svg class="w-6 h-6  dark:text-white text-green-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 11.917 9.724 16.5 19 7.5"/>
  </svg>
    const Wrong = () => <span className="text-red-600">✘</span>

    // Validators
    const hasUpper = /[A-Z]/.test(password)
    const hasLower = /[a-z]/.test(password)
    const hasDigit = /[\d]/.test(password)
    const hasSymbol = /[~`!@#$%^&*()_+=\-\\|\]\}\[\{'";:\/\?\.>,<\}\]]/.test(password)
    const between = password.length >= 8 && password.length <= 16
    const match = password === passwordConfirmation

    // console.log('hasUpper', hasUpper)

    if (password === '') {
        return <small className="text-xs">8-16 mix of Upper, Lower, Digit, and Symbol</small>
    }


    return (
        <div className="text-xs">
            <div className="text-xs flex flex-wrap justify-between">

                <p className="flex gap-2">
                    {hasUpper ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Uppercase</span>
                </p>
                <p className="flex gap-2">
                    {hasLower ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Lowercase</span>
                </p>
                <p className="flex gap-2">
                    {hasDigit ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Number</span>
                </p>
                <p className="flex gap-2">
                    {hasSymbol ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Symbol</span>
                </p>
                <p className="flex gap-2">
                    {between ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Between 8 - 16</span>
                </p>
                <p className="flex gap-2">
                    {match ? <Correct /> : <Wrong />}
                    <span className="text-gray-300">Match</span>
                </p>
            </div>
        </div>
    )

}

export default memo(PasswordValidator)