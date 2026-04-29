from app.models.inventory import Inventory


def generate_inventory_ini(inventory: Inventory) -> str:
    """Build an Ansible INI inventory from an Inventory ORM object."""
    lines = ["[all]"]
    for host in inventory.hosts:
        vars_: list[str] = [f"ansible_host={host.address}"]
        if host.connection_type.value == "winrm":
            vars_.append("ansible_connection=winrm")
            vars_.append(f"ansible_port={host.port or 5985}")
            vars_.append("ansible_winrm_transport=basic")
        else:
            vars_.append("ansible_connection=ssh")
            if host.port:
                vars_.append(f"ansible_port={host.port}")
        lines.append(f"{host.name} " + " ".join(vars_))
    return "\n".join(lines) + "\n"
