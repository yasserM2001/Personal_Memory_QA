import { memo } from "react";

function MobileValidator({mobile}) {
    
    console.log('MobileValidator component rendered');
    
    const patt = /^01[0125][0-9]{8}$/
    const Len = () => <span className="text-sky-500 text-xs">Enter a mobile number with this format 01*********</span>
    const Invalid = () => <span className="text-red-500">invalid mobile number</span>
    const Valid = () => <span className="text-green-500">Valid mobile number</span>
    const isValid = patt.test(mobile);
    return (
        <div>
            <p className="flex justify-between flex-col text-xs">
                {(mobile.length <11) ? <Len/> : ((mobile.length === 11) && isValid)? <Valid/> :<Invalid/>}
            </p>
        </div>
    )
}
export default memo(MobileValidator)