import time

import click
import sunspec.core.client

import epcsunspecdemo.clishared
import epcsunspecdemo.utils


def send_val(point, val):
    point.value_setter(val)
    point.write()


def gridtied_demo(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )
    cmd_point = device.epc_control.model.points['CmdBits']
    # Read common model
    device.common.read()
    print(device.common)

    device.serial.read()
    print(device.serial)

    device.epc_control.read()
    print(device.epc_control)
    # Set Mobus as control source 0=CAN 1=Modbus
    send_val(device.epc_control.model.points['CtlSrc'], 1)

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        val = cmd_bits.set('InvertHwEnable')

    send_val(cmd_point, val)
    # clear faults
    send_val(cmd_point, cmd_bits.set('FltClr'))
    # remove fault clear command
    send_val(cmd_point, cmd_bits.clear('FltClr'))

    send_val(device.epc_control.model.points['CmdV'], 480)
    send_val(device.epc_control.model.points['CmdHz'], 60)

    try:
        for _ in range(cycles):
            # enable and run
            val = cmd_bits.set('En')
            send_val(cmd_point, val)
            print('{}: {}'.format(val, cmd_bits.active()))
            send_val(device.epc_control.model.points['CmdRealPwr'], 10000) #10kW
            send_val(device.epc_control.model.points['CmdReactivePwr'], 5000) #5kVA

            device.epc_control.read()
            print(device.epc_control)

            time.sleep(0.5)
    finally:
        # remove run command
        send_val(cmd_point, cmd_bits.clear('En'))
        # return control to CAN:
        send_val(device.epc_control.model.points['CtlSrc'], 0)

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
    cmd_point = device.epc_control.model.points['CmdBits']

    # Read common model
    device.common.read()
    print(device.common)

    print(device.models)

    device.epc_control.read()
    print(device.epc_control)
    fault_bits.from_int(device.epc_control.FaultFlags)
    print('Faults: ' + str(fault_bits.active()))
    # Set Mobus as control source 0=CAN 1=Modbus
    send_val(device.epc_control.model.points['CtlSrc'], 1)

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        val = cmd_bits.set('InvertHwEnable')

    send_val(cmd_point, val)
    # clear faults
    send_val(cmd_point, cmd_bits.set('FltClr'))
    # remove fault clear command
    send_val(cmd_point, cmd_bits.clear('FltClr'))

    status_bits.from_int(device.epc_control.Evt1)
    fault_bits.from_int(device.epc_control.FaultFlags)
    warning_bits.from_int(device.epc_control.WrnFlgs)

    print('Cmd bits: ' + str(cmd_bits.active()))
    print('Evt1: ' + str(status_bits.active()))
    print('Faults: ' + str(fault_bits.active()))
    print('Warnings: ' + str(warning_bits.active()))

    try:
        for _ in range(cycles):
            # enable and run
            send_val(cmd_point, cmd_bits.set('En'))
            send_val(device.epc_control.model.points['CmdVout'], 800)

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
        send_val(cmd_point, cmd_bits.clear('En'))
        # return control to CAN:
        send_val(device.epc_control.model.points['CtlSrc'], 0)

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
