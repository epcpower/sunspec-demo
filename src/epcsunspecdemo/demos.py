import time

import epcsunspecdemo.utils


def update_cmd_bits(cmd_bits, device):
    device.epc_control.CmdBits = cmd_bits.to_int()
    print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
    device.epc_control.model.points['CmdBits'].write()
    device.epc_control.read()
    print(device.epc_control)
    time.sleep(0.5)
    device.inverter.read()
    print(device.inverter.StVnd)


def gridtied(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )

    # Read common model
    device.common.read()
    print(device.common)

    device.model_17.read()
    print(device.model_17)

    # Set Mobus as control source 0=CAN 1=Modbus
    device.epc_control.read()
    print(device.epc_control)
    device.epc_control.CtlSrc = 1
    device.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        cmd_bits.set('InvertHwEnable')
    else:
        cmd_bits.clear('InvertHwEnable')

    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # clear faults
    cmd_bits.set('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # remove fault clear command
    cmd_bits.clear('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    device.epc_control.CmdV = 480
    device.epc_control.CmdHz = 60
    device.epc_control.model.points['CmdV'].write()
    device.epc_control.model.points['CmdHz'].write()

    try:
        for _ in range(cycles):
            # enable and run
            cmd_bits.set('En')
            device.epc_control.CmdBits = cmd_bits.to_int()
            print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
            device.epc_control.CmdRealPwr = 10000  # 10kW
            device.epc_control.CmdReactivePwr = 5000  # 5kVA
            device.epc_control.model.points['CmdBits'].write()
            device.epc_control.model.points['CmdRealPwr'].write()
            device.epc_control.model.points['CmdReactivePwr'].write()

            device.epc_control.read()
            print(device.epc_control)

            time.sleep(0.5)
    finally:
        # remove run command
        cmd_bits.clear('En')
        update_cmd_bits(cmd_bits=cmd_bits, device=device)

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")


def dcdc(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )
    status_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='Evt1',
    )
    fault_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='FaultFlags',
    )
    warning_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='WrnFlgs',
    )

    # Read common model
    device.common.read()
    print(device.common)

    print(device.models)

    # Set Mobus as control source 0=CAN 1=Modbus
    device.epc_control.read()
    print(device.epc_control)
    fault_bits.from_int(device.epc_control.FaultFlags)
    print('Faults: ' + str(fault_bits.active()))
    device.epc_control.CtlSrc = 1
    device.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        cmd_bits.set('InvertHwEnable')
    else:
        cmd_bits.clear('InvertHwEnable')

    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # clear faults
    cmd_bits.set('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # remove fault clear command
    cmd_bits.clear('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    status_bits.from_int(device.epc_control.Evt1)
    fault_bits.from_int(device.epc_control.FaultFlags)
    warning_bits.from_int(device.epc_control.WrnFlgs)

    print('Cmd bits: ' + str(cmd_bits.active()))
    print('Evt1: ' + str(status_bits.active()))
    print('Faults: ' + str(fault_bits.active()))
    print('Warnings: ' + str(warning_bits.active()))

    device.epc_control.CmdVout = 800
    try:
        for _ in range(cycles):
            # enable and run
            cmd_bits.set('En')
            device.epc_control.CmdBits = cmd_bits.to_int()
            # print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
            device.epc_control.model.points['CmdBits'].write()
            device.epc_control.model.points['CmdVout'].write()

            device.epc_control.read()
            status_bits.from_int(device.epc_control.Evt1)
            fault_bits.from_int(device.epc_control.FaultFlags)
            warning_bits.from_int(device.epc_control.WrnFlgs)
            print('State: ' + str(device.epc_control.St))
            print('Evt1: ' + str(status_bits.active()))
            print('Faults: ' + str(fault_bits.active()))
            print('Warnings: ' + str(warning_bits.active()))
            # print(device.epc_control)

            # time.sleep(0.5)
    finally:
        # remove run command
        cmd_bits.clear('En')
        update_cmd_bits(cmd_bits=cmd_bits, device=device)

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")
