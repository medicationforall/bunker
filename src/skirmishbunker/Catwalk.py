import cadquery as cq
from skirmishbunker import Base

class Catwalk(Base):
    def __init__(self):
        super().__init__()
        self.length = 187
        self.width = 187
        self.height = 4
        self.chamfer_distance = 1

        self.interior_length = 130
        self.interior_width = 130
        self.interior_height = 2
        self.interior_overlap = 5

        self.render_magnets = True
        self.magnet_radius = 1.5
        self.magnet_height = 2
        self.magnet_padding = 1.5
        self.fit_padding = .4

        self.render_corner_walls =  True
        self.wall_height = 25
        self.wall_length = 55
        self.wall_width = 3

        self.platform = None
        self.cut_magnets = None
        self.corner_walls = None

    def __make_platform(self):
        platform = (
            cq.Workplane("XY")
            .box(self.length, self.width, self.height)
            .faces("-Z").chamfer(self.height-.1)
        )
        center_cut = (
            cq.Workplane("XY")
            .box(
                self.interior_length + self.fit_padding,
                self.interior_width + self.fit_padding,
                self.height
            )
        )
        overlap = (
            cq.Workplane("XY")
            .box(
                self.interior_length + self.fit_padding ,
                self.interior_width + self.fit_padding,
                self.interior_height
            )
        )
        overlap_cut = (
            cq.Workplane("XY")
            .box(
                self.interior_length - self.interior_overlap*2,
                self.interior_width - self.interior_overlap*2,
                self.interior_height
            )
        )

        self.platform = (
            platform
            .cut(center_cut)
            .union(overlap.translate((0,0,-1*(self.height/2 - self.interior_height/2))))
            .cut(overlap_cut.translate((0,0,-1*(self.height/2 - self.interior_height/2))))
        )

    def __make_magnet_cuts(self):
        magnet = cq.Workplane("XY").cylinder(self.magnet_height, self.magnet_radius+.1)

        x_translate = self.interior_length/2-self.magnet_radius-self.magnet_padding
        y_translate = self.interior_width/2-self.magnet_radius-self.magnet_padding
        z_translate = -1*(self.height/2 - self.magnet_height/2)

        pips = (
            cq.Workplane("XY")
            .union(magnet.translate((x_translate, y_translate, z_translate)))
            .union(magnet.translate((-1*x_translate, y_translate, z_translate)))
            .union(magnet.translate((-1*x_translate, -1*y_translate, z_translate)))
            .union(magnet.translate((x_translate, -1*y_translate, z_translate)))
        )
        self.cut_magnets = pips

    def __make_corner_walls(self):
        wall = (
            cq.Workplane("XY")
            .box(
                self.wall_length,
                self.wall_width,
                self.wall_height
            )
            .faces("Z").edges("<X").chamfer(self.wall_height/2)
        )

        corner = (
            cq.Workplane("XY")
            .union(wall.translate((-1*(self.wall_length/2-self.wall_width/2),0,0)))
            .union(
                wall
                .translate((-1*(self.wall_length/2-self.wall_width/2),0,0))
                .rotate((0,0,1),(0,0,0),90)
            )
            .translate((
                self.length/2-self.wall_width/2,
                -1*(self.width/2-self.wall_width/2),
                self.wall_height/2+self.height/2
            ))
        )

        corners = (
            cq.Workplane("XY")
            .union(corner)
            .union(corner.rotate((0,0,1),(0,0,0), 90))
            .union(corner.rotate((0,0,1),(0,0,0), 180))
            .union(corner.rotate((0,0,1),(0,0,0), -90))
        )
        self.corner_walls = corners

    def make(self):
        super().make()
        self.__make_platform()

        if self.render_magnets:
            self.__make_magnet_cuts()

        if self.render_corner_walls:
            self.__make_corner_walls()

    def build(self):
        super().build()
        scene = (
            cq.Workplane("XY")
            .union(self.platform)
        )

        if self.render_magnets and self.cut_magnets:
            scene = scene.cut(self.cut_magnets)

        if self.render_corner_walls and self.corner_walls:
            scene = scene.union(self.corner_walls)

        return scene


#bp = Catwalk()
#bp.make()
#result = bp.build()

#show_object(result)