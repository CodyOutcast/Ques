import React, { useEffect, useRef, useState } from 'react';
import Matter from 'matter-js';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { X } from 'lucide-react';
import { motion } from 'framer-motion';

interface PhysicsTagContainerProps {
  tags: string[];
  onRemoveTag: (index: number) => void;
  containerHeight?: number;
  tagColor?: 'default' | 'green' | 'blue' | 'purple';
  emptyText?: string;
}

interface PhysicsTag {
  id: string;
  text: string;
  body: Matter.Body;
  index: number;
}

export function PhysicsTagContainer({ 
  tags, 
  onRemoveTag, 
  containerHeight = 300,
  tagColor = 'default',
  emptyText = 'Tags will drop here'
}: PhysicsTagContainerProps) {
  const sceneRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<Matter.Engine | null>(null);
  const renderRef = useRef<Matter.Render | null>(null);
  const runnerRef = useRef<Matter.Runner | null>(null);
  const physicsTagsRef = useRef<PhysicsTag[]>([]);
  const [physicsTags, setPhysicsTags] = useState<PhysicsTag[]>([]);
  const [tagPositions, setTagPositions] = useState<Map<string, { x: number; y: number; rotation: number }>>(new Map());
  const animationFrameRef = useRef<number>();

  // 获取标签颜色样式
  const getTagColorClass = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'blue':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'purple':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      default:
        return '';
    }
  };

  useEffect(() => {
    if (!sceneRef.current) return;

    const width = sceneRef.current.clientWidth;
    const height = containerHeight;

    // 创建引擎
    const engine = Matter.Engine.create({
      gravity: { x: 0, y: 1 },
      enableSleeping: true, // 启用睡眠机制，让静止物体停止更新
      constraintIterations: 2, // 约束求解迭代次数
      positionIterations: 6, // 位置求解迭代次数，提高碰撞精度
      velocityIterations: 4 // 速度求解迭代次数
    });
    engineRef.current = engine;

    // 创建渲染器（隐藏，仅用于物理计算）
    const render = Matter.Render.create({
      element: sceneRef.current,
      engine: engine,
      options: {
        width: width,
        height: height,
        wireframes: false,
        background: 'transparent',
        // 完全隐藏 canvas
        pixelRatio: 1
      }
    });
    renderRef.current = render;

    // 隐藏 canvas
    if (render.canvas) {
      render.canvas.style.display = 'none';
    }

    // 创建边界 - 适中摩擦力，保持堆叠
    const wallOptions = { 
      isStatic: true, 
      friction: 0.4, 
      frictionStatic: 0.6,
      restitution: 0.1 
    };
    // 地面抬高一点，给阴影留出空间
    const ground = Matter.Bodies.rectangle(width / 2, height - 10, width, 50, wallOptions);
    const leftWall = Matter.Bodies.rectangle(-25, height / 2, 50, height, wallOptions);
    const rightWall = Matter.Bodies.rectangle(width + 25, height / 2, 50, height, wallOptions);
    
    Matter.World.add(engine.world, [ground, leftWall, rightWall]);

    // 使用 Runner 运行引擎
    const runner = Matter.Runner.create();
    runnerRef.current = runner;
    Matter.Runner.run(runner, engine);

    // 更新循环
    const updateLoop = () => {
      const newPositions = new Map<string, { x: number; y: number; rotation: number }>();
      
      physicsTagsRef.current.forEach(tag => {
        newPositions.set(tag.id, {
          x: tag.body.position.x,
          y: tag.body.position.y,
          rotation: tag.body.angle
        });
      });
      
      setTagPositions(newPositions);
      animationFrameRef.current = requestAnimationFrame(updateLoop);
    };
    
    updateLoop();

    // 清理函数
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (runnerRef.current && engineRef.current) {
        Matter.Runner.stop(runnerRef.current);
        runnerRef.current = null;
      }
      if (renderRef.current) {
        Matter.Render.stop(renderRef.current);
        if (renderRef.current.canvas) {
          renderRef.current.canvas.remove();
        }
        renderRef.current = null;
      }
      if (engineRef.current) {
        Matter.Engine.clear(engineRef.current);
        engineRef.current = null;
      }
    };
  }, [containerHeight]);

  // 处理标签的添加和移除
  useEffect(() => {
    if (!engineRef.current || !sceneRef.current) return;

    const width = sceneRef.current.clientWidth;
    const existingTagIds = new Set(physicsTagsRef.current.map(t => t.text));
    const currentTagTexts = new Set(tags);

    // 移除不存在的标签
    physicsTagsRef.current = physicsTagsRef.current.filter(tag => {
      if (!currentTagTexts.has(tag.text)) {
        Matter.World.remove(engineRef.current!.world, tag.body);
        return false;
      }
      return true;
    });

    // 添加新标签
    tags.forEach((tagText, index) => {
      if (!existingTagIds.has(tagText)) {
        // 计算标签尺寸（近似）
        const charWidth = 8;
        const padding = 24;
        const tagWidth = Math.min(Math.max(tagText.length * charWidth + padding, 60), 150);
        const tagHeight = 28;

        // 随机 x 位置，从顶部掉落
        const randomX = Math.random() * (width - tagWidth) + tagWidth / 2;
        const startY = -50; // 从顶部上方开始

        // 创建物理物体 - 温和的弹跳效果，保持可读性和堆叠效果
        const body = Matter.Bodies.rectangle(randomX, startY, tagWidth, tagHeight, {
          restitution: 0.15, // 极小的弹性
          friction: 0.3, // 适中摩擦力，保持堆叠效果
          density: 0.002, // 增加密度，更稳定
          frictionAir: 0.03, // 适度空气阻力
          frictionStatic: 0.5, // 适中静摩擦力
          angle: (Math.random() - 0.5) * 0.05, // 更小的初始旋转
          inertia: Infinity, // 禁止旋转，保持标签水平
          chamfer: { radius: 4 },
          slop: 0.01, // 减小碰撞容差，避免穿透
          sleepThreshold: 15 // 快速进入睡眠状态
        });

        // 添加到世界
        Matter.World.add(engineRef.current!.world, body);

        const newTag = {
          id: `${tagText}-${Date.now()}-${Math.random()}`,
          text: tagText,
          body: body,
          index: index
        };

        // 添加到追踪列表
        physicsTagsRef.current.push(newTag);
      }
    });

    // 同步到 state 以触发重新渲染
    setPhysicsTags([...physicsTagsRef.current]);
  }, [tags]);

  const handleRemove = (tagText: string) => {
    const originalIndex = tags.indexOf(tagText);
    if (originalIndex !== -1) {
      // 找到要删除的标签
      const tagToRemove = physicsTagsRef.current.find(t => t.text === tagText);
      
      if (tagToRemove && engineRef.current) {
        // 唤醒所有其他标签，让它们能够下落
        physicsTagsRef.current.forEach(tag => {
          if (tag.id !== tagToRemove.id) {
            Matter.Sleeping.set(tag.body, false);
          }
        });
      }
      
      onRemoveTag(originalIndex);
    }
  };

  return (
    <div className="relative w-full overflow-hidden" style={{ height: `${containerHeight}px` }}>
      {/* 物理引擎场景（隐藏） */}
      <div ref={sceneRef} className="absolute inset-0 pointer-events-none" />
      
      {/* 渲染的标签 - 允许底部阴影溢出 */}
      <div className="absolute inset-0" style={{ 
        overflowX: 'hidden',
        overflowY: 'visible',
        paddingBottom: '15px' // 给底部阴影留空间
      }}>
        {physicsTags.map((tag) => {
          const position = tagPositions.get(tag.id);
          if (!position) return null;

          return (
            <div
              key={tag.id}
              className="absolute"
              style={{
                left: `${position.x}px`,
                top: `${position.y}px`,
                transform: `translate(-50%, -50%) rotate(${position.rotation}rad)`,
                transition: 'none',
                pointerEvents: 'auto',
                willChange: 'transform',
                zIndex: 10
              }}
            >
              <Badge 
                variant="outline" 
                className={`pr-1 text-xs whitespace-nowrap shadow-lg hover:shadow-xl transition-shadow ${getTagColorClass(tagColor)}`}
                style={{
                  cursor: 'grab',
                  userSelect: 'none'
                }}
              >
                <span className="max-w-[120px] truncate">{tag.text}</span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-3 w-3 p-0 ml-1 hover:bg-red-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(tag.text);
                  }}
                >
                  <X size={8} />
                </Button>
              </Badge>
            </div>
          );
        })}
      </div>

      {/* 空状态提示 */}
      {tags.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <p className="text-sm text-gray-400">{emptyText}</p>
        </div>
      )}
    </div>
  );
}

