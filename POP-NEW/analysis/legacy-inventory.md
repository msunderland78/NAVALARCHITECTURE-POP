# Legacy Inventory

## Files Reviewed

| File | Size | Type | SHA-256 | Initial Assessment |
|---|---:|---|---|---|
| `POP.EXE` | 81920 | PE32 executable, Win32 GUI, Intel 80386 | `effcebe1df92a2f4331a682a47b5b9860ca0ed98f8a77ae7e5a0c02a36ed4435` | Visual C++ 6 MFC interface shell |
| `POPFTRN.EXE` | 264192 | PE32 executable, Win32 console, Intel 80386 | `4916b84dc3fa18c4583be28624f2ce409aa659b0c8fbdd779d64212e8e155336` | DEC or Visual Fortran numerical engine |
| `POP1.POP` | 9728 | OLE Compound Document | `8a01a465ae0d2b848c0f155f15c7650be47f7c4df74dcde1daacfccc9fe09c63` | Saved sample document with input and report text |
| `POPout.pop` | 12800 | OLE Compound Document | `4e87b676fb23f9ffa0647db3b74727cea752e3b6f712587d52fe3d401095fc38` | Saved sample document with duplicated output/report state |
| `fort.9` | 224 | ASCII text, CRLF line endings | `902411cb88f1777df77b9330feaaf2a681aebd693cd0adbf93792b0234824e10` | Fortran diagnostic trace |

## Current Conclusions

`POP.EXE` is not the calculation engine. It is a Windows MFC document application that collects inputs, manages `.POP` files, invokes `POPFTRN.EXE`, reads output, and plots results.

`POPFTRN.EXE` contains the numerical work. Its visible runtime strings identify a DEC Fortran runtime message catalog from January 7, 1997, and its output labels match the propeller optimization report in the `.POP` files.

The current artifacts do not show evidence of hardware lock enforcement. No HASP, Sentinel, Rainbow, Wibu, CodeLock, Aladdin, or SafeNet indicators were found in strings or import tables.

## Preservation Rules

The files in `POP-OLD` are archival inputs. They are ignored by git and must not be modified. All derived notes, fixtures, source code, and tests belong under `POP-NEW`.
