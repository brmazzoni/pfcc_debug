# PFCC debug tools

## IP addresses


`172.28.1.XYZ` or `172.254.1.XYZ` where:
- `X`: 1 dataloader IP, 2 for default IPs???
- `Y`: 0 for COM Lane, 1 for MON Lane
- `Z`: 1 for PFCC1, 2 for PFCC2, 3 for PFCC3

## Checking PFCC configuration

```
binary_udp_loader <IP> {COM|MON} REV
```

## Getting fault log

```
platform_error_handle -ip <IP> -trg {PFCC_COM|PFCC_MON}
```

## Read the trace

```
traceread -ip <IP> -trg {PFCC_COM|PFCC_MON} -file <output_file, e.g. com_sump.bin>
```