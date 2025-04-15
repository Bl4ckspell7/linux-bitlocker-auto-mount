#!/bin/bash
# Unmount all mounted dislocker volumes and their associated media mounts

for mountpoint in /media/"$USER"/*; do
    if mountpoint -q "$mountpoint"; then
        echo "Unmounting $mountpoint"
        umount -l "$mountpoint"
    fi
done

for dis_mount in /mnt/dislocker/*; do
    if mountpoint -q "$dis_mount"; then
        echo "Killing dislocker and unmounting $dis_mount"
        umount -l "$dis_mount"
    fi
done
