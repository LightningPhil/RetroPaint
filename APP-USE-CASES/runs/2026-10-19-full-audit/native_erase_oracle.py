"""Elementary 8-bit associated-colour laws; no application imports."""
import numpy as np

def associated_bytes(rgba):
    a=np.asarray(rgba,dtype=np.int64).reshape(-1,4)
    out=a.copy()
    # Recover integer premultiplied bytes from PNG's straight RGB. Division by
    # odd255 has no half-integer ties;127 implements nearest integer exactly.
    out[:,:3]=(a[:,:3]*a[:,3,None]+127)//255
    return out

def destination_out_valid(before,after):
    """One shared inverse coverage factor, each component quantized to 8 bits.

    For component b>0, a one-byte native quantization interval constrains the
    same q to [(a-1)/b,(a+1)/b]. Check all interval intersections with integer
    cross products, so no floating tolerance is introduced. Colour/alpha cannot
    increase and zero source components cannot gain pigment. Apply this law at
    each actual operation; rounding is not assumed to happen only once per path.
    """
    b=associated_bytes(before);a=associated_bytes(after);valid=np.all((a<=b)&((b!=0)|(a==0)),axis=1)
    for i in range(4):
        for j in range(4):
            pair=(b[:,i]>0)&(b[:,j]>0)
            valid&=(~pair)|((a[:,i]-1)*b[:,j]<=(a[:,j]+1)*b[:,i])
    return valid
