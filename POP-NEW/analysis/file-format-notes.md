# File Format Notes

## Executables

`POP.EXE` and `POPFTRN.EXE` are both PE32 files for 32-bit Windows.

`POP.EXE` imports:

- `MFC42.DLL`
- `MSVCRT.dll`
- `MSVCIRT.dll`
- `KERNEL32.dll`
- `USER32.dll`
- `GDI32.dll`

`POPFTRN.EXE` imports:

- `KERNEL32.dll`

The Fortran runtime appears mostly statically linked into `POPFTRN.EXE`.

## `.POP` Documents

`POP1.POP` and `POPout.pop` are OLE Compound Document files. The visible streams are:

- `Root Entry`
- `Contents`

`POP1.POP` also exposes a temporary stream name:

- `emp\~DFFD25.tmp`

The `Contents` stream appears to contain MFC serialized document state. It is not a simple text file, but useful labels and values are recoverable from printable strings.

The new product should use JSON as its native format. Legacy `.POP` import should be implemented as a compatibility adapter that reads the OLE `Contents` stream, extracts known labels, and converts the result into the native JSON model.

## Temporary Files

The legacy GUI references these files or commands:

- `Out`
- `POPG`
- `POPGR`
- `del Out`
- `del Popgr`
- `POPFTRN.exe`

The likely protocol is:

1. GUI deletes stale temporary output.
2. GUI invokes `POPFTRN.exe`.
3. Fortran engine writes report data to `Out`.
4. Fortran engine writes plot data to `POPG` or `POPGR`.
5. GUI reads the temporary files.

The Linux web application should not recreate this temporary-file protocol. The backend should call calculation functions directly and return structured results.

## `fort.9`

`fort.9` contains eight optimizer diagnostic lines:

```text
 ***RESET RK=   2048.00***
 ***RESET RK=   4096.00***
 ***RESET RK=   8192.00***
 ***RESET RK=  16384.00***
 ***RESET RK=  32768.00***
 ***RESET RK=  65536.00***
 ***RESET RK= 131072.00***
 ***RESET RK= 262144.00***
```

This is probably an internal optimizer trace. It should be preserved for analysis but not exposed as primary product behavior.
