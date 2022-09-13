import enum
import os
import struct


class ShapeType(enum.IntEnum):
    POLYGON = 5,


def read_shape_file(file_name: str) -> list:
    polygons = list()
    with open(file_name, mode="rb") as fh:
        # Read 100 bytes of header
        file_code, = struct.unpack(">i", fh.read(4))[:1]
        assert file_code == 0x0000270a
        fh.seek(24)  # skip past unused values to file length record
        file_length, = struct.unpack(">i", fh.read(4))
        version, shape_type = struct.unpack("<2i", fh.read(8))
        shape_type = ShapeType(int(shape_type))
        assert shape_type == ShapeType.POLYGON
        print(file_length, version, shape_type)
        file_end = 2 * file_length
        assert file_end > 0
        fh.seek(100)  # skip to end of header
        # Read records one at a time
        while fh.tell() < file_end:
            record_number, record_length = struct.unpack(">2i", fh.read(8))
            assert record_length > 0
            # print(record_number, record_length)
            next_record = fh.tell() + 2 * record_length
            record_shape_type, = struct.unpack("<i", fh.read(4))
            record_shape_type = ShapeType(record_shape_type)
            assert record_shape_type == shape_type
            # TODO: polygon-specific subroutine
            assert record_shape_type == ShapeType.POLYGON
            fh.seek(32, os.SEEK_CUR)  # skip MBR minimum bounding rectangle
            num_rings, num_points = struct.unpack("<2i", fh.read(8))
            # print("  ", num_rings, num_points)
            ring_indexes = struct.unpack(f"<{num_rings}i", fh.read(4 * num_rings))
            coordinates = struct.unpack(f"<{num_points * 2}d", fh.read(16 * num_points))
            lon_coords = coordinates[::2]
            lat_coords = coordinates[1::2]
            # TODO: test a multi-ring shape file
            rings = list()
            for ring in range(num_rings):
                first_index = ring_indexes[ring]
                if ring >= num_rings - 1:
                    point_count = num_points - first_index  # final ring in polygon
                else:
                    point_count = ring_indexes[ring + 1] - first_index
                assert point_count > 0
                point_list = list()
                for point in range(point_count):
                    ix = first_index + point
                    point_list.append((lon_coords[ix], lat_coords[ix]))
                rings.append(point_list)
            fh.seek(next_record)
            polygons.append(rings)
    return polygons


if __name__ == "__main__":
    f_name = "C:/Users/cmbruns/Downloads/gshhg-shp-2.3.7/GSHHS_shp/c/GSHHS_c_L6.shp"
    polygons = read_shape_file(f_name)
    print(polygons)
