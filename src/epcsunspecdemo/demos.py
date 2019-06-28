import time

import click
import sunspec.core.client

import epcsunspecdemo.clishared
import epcsunspecdemo.utils


def gridtied_demo(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )

    # Read common model
    device.common.read()
    print(device.common)

    device.serial.read()
    print(device.serial)

    # Set Mobus as control source 0=CAN 1=Modbus
    device.epc_control.read()
    print(device.epc_control)
    device.epc_control.CtlSrc = 1
    device.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        device.epc_control.CmdBits = cmd_bits.set('InvertHwEnable')
    else:
        device.epc_control.CmdBits = cmd_bits.clear('InvertHwEnable')

    device.epc_control.model.points['CmdBits'].write()

    # clear faults
    device.epc_control.CmdBits = cmd_bits.set('FltClr')
    device.epc_control.model.points['CmdBits'].write()

    # remove fault clear command
    device.epc_control.CmdBits = cmd_bits.clear('FltClr')
    device.epc_control.model.points['CmdBits'].write()

    device.epc_control.CmdV = 480
    device.epc_control.CmdHz = 60
    device.epc_control.model.points['CmdV'].write()
    device.epc_control.model.points['CmdHz'].write()

    try:
        for _ in range(cycles):
            # enable and run
            device.epc_control.CmdBits = cmd_bits.set('En')
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
        device.epc_control.CmdBits = cmd_bits.clear('En')
        device.epc_control.model.points['CmdBits'].write()

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")


def dcdc_demo(device, invert_enable, cycles):
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
        device.epc_control.CmdBits = cmd_bits.set('InvertHwEnable')
    else:
        device.epc_control.CmdBits = cmd_bits.clear('InvertHwEnable')

    device.epc_control.model.points['CtlSrc'].write()

    # clear faults
    device.epc_control.CmdBits = cmd_bits.set('FltClr')
    device.epc_control.model.points['CtlSrc'].write()

    # remove fault clear command
    device.epc_control.CmdBits = cmd_bits.clear('FltClr')
    device.epc_control.model.points['CtlSrc'].write()

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
            device.epc_control.CmdBits = cmd_bits.set('En')
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
        device.epc_control.CmdBits = cmd_bits.clear('En')
        device.epc_control.model.points['CtlSrc'].write()

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")


@click.group(
    help='Demo connection to a grid-tied converter',
)
@click.pass_obj
def gridtied(config):
    config.common = gridtied_demo


@click.group(
    help='Demo connection to a DCDC converter',
)
@click.pass_obj
def dcdc(config):
    config.common = dcdc_demo


invert_enable_option = click.option(
    '--invert-enable/--no-invert-enable',
    help='Invert the converters hardware enable input',
)

cycles_option = click.option(
    '--cycles',
    type=int,
    default=25,
    help='Number of demo cycles to run',
)


@click.command(
    help='Demo direct serial Modbus RTU connection',
)
@epcsunspecdemo.clishared.serial_port_option
@epcsunspecdemo.clishared.serial_baudrate_option
@epcsunspecdemo.clishared.timeout_option
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@epcsunspecdemo.clishared.slave_id_option
@cycles_option
@click.pass_obj
def serial(
        config,
        port,
        timeout,
        model_path,
        invert_enable,
        slave_id,
        baudrate,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            device_type=sunspec.core.client.RTU,
            name=port,
            baudrate=baudrate,
            timeout=timeout,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


@click.command(
    help='Demo Modbus TCP connection',
)
@epcsunspecdemo.clishared.tcp_address_option
@epcsunspecdemo.clishared.tcp_port_option
@epcsunspecdemo.clishared.timeout_option
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@epcsunspecdemo.clishared.slave_id_option
@cycles_option
@click.pass_obj
def tcp(
        config,
        address,
        port,
        timeout,
        model_path,
        invert_enable,
        slave_id,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            device_type=sunspec.core.client.TCP,
            ipaddr=address,
            ipport=port,
            timeout=timeout,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


def add_commands(group):
    group.add_command(gridtied, name='gridtied')
    group.add_command(dcdc, name='dcdc')

    for group in (gridtied, dcdc):
        group.add_command(serial)
        group.add_command(tcp)
